import json
from datetime import timedelta

import folium
from folium.plugins import Fullscreen, LocateControl
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.views.decorators.http import require_POST

from MerchantSideApp.models import Meal, Restaurant
from RecommendationSystem.services import (
    get_recommendation_cooldown_days,
    record_user_choice,
)

from ..auth_utils import get_current_user, user_login_required
from ..forms import (
    AccountProfileForm,
    FavoriteForm,
    MealRecordForm,
    NotificationSettingFormSet,
    PasswordChangeForm,
    RecommendationFilterForm,
    RestaurantSearchForm,
    ReviewForm,
    UserPreferenceForm,
)
from ..models import (
    DailyMealRecord,
    Favorite,
    MealComponent,
    NotificationLog,
    NotificationSetting,
    Review,
    UserPreference,
)
from ..services import (
    RecommendationEngine,
    build_health_summary,
    ensure_notification_settings,
    log_meal_record_notification,
    recalculate_weekly_summary,
    summarize_today,
)


DEFAULT_MAP_CENTER = (23.6978, 120.9605)
MAX_MAP_RESULTS = 50
MAX_MEAL_RESULTS = 40


def _serialize_components(record: DailyMealRecord) -> str:
    component_qs = record.components.all()
    return json.dumps(
        [
            {
                "name": component.name,
                "quantity": component.quantity or "",
                "calories": str(component.calories),
            }
            for component in component_qs
        ],
        ensure_ascii=False,
    )


def _save_components(record: DailyMealRecord, components_data):
    MealComponent.objects.filter(meal_record=record).delete()
    if not components_data:
        return
    MealComponent.objects.bulk_create(
        [
            MealComponent(
                meal_record=record,
                name=component["name"],
                quantity=component.get("quantity"),
                calories=component.get("calories", 0),
            )
            for component in components_data
        ]
    )


def _render(request, template_name: str, active_nav: str, extra: dict | None = None):
    context = {
        "active_nav": active_nav,
        "current_user": get_current_user(request),
    }
    if extra:
        context.update(extra)
    return render(request, template_name, context)


def _build_recommendation_cards(meals, reason: str, used_ids: set[int] | None = None):
    used_ids = used_ids or set()
    cards = []
    for meal in meals:
        if meal.id in used_ids:
            continue
        cards.append(
            {
                "meal": meal,
                "restaurant": meal.restaurant,
                "favorite_count": getattr(meal, "favorite_count", 0) or 0,
                "reason": reason,
            }
        )
        used_ids.add(meal.id)
    return cards


def _serialize_card(card: dict) -> dict:
    meal = card["meal"]
    restaurant = card["restaurant"]
    price_label = ""
    if getattr(restaurant, "price_range", None):
        try:
            price_label = restaurant.get_price_range_display()
        except Exception:  # pragma: no cover - defensive
            price_label = restaurant.price_range
    meal_url = reverse("merchantsideapp:meal_detail", args=[meal.id])
    restaurant_url = reverse("merchantsideapp:restaurant_detail", args=[restaurant.id])
    return {
        "meal": {
            "id": meal.id,
            "name": meal.name,
            "description": meal.description or "",
            "isVegetarian": bool(meal.is_vegetarian),
            "isSpicy": bool(meal.is_spicy),
            "url": meal_url,
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "cuisineType": restaurant.cuisine_type or "",
            "priceRange": restaurant.price_range or "",
            "priceLabel": price_label or "",
            "city": restaurant.city or "",
            "district": restaurant.district or "",
            "url": restaurant_url,
        },
        "favoriteCount": card.get("favorite_count", 0),
        "reason": card.get("reason") or "",
    }


def _collect_form_errors(form) -> dict:
    if not form.is_bound or form.is_valid():
        return {}
    errors = {}
    for field, field_errors in form.errors.items():
        errors[field] = [str(error) for error in field_errors]
    return errors


def _build_random_context(user, data=None):
    engine = RecommendationEngine(user)
    preference = getattr(user, "preferences", None)
    initial_data = engine.initial_data(preference)
    filter_form = RecommendationFilterForm(initial=initial_data)
    filters_used = engine.filters_from_data(initial_data)
    primary_reason = "根據你的偏好"
    primary_meals = []
    recommendation_alert = None
    action = (data or {}).get("action") if data else None
    cooldown_days = get_recommendation_cooldown_days(user)

    if data:
        if action == "use_preferences":
            filters_used = engine.filters_from_preferences(preference, (data or {}).get("limit"))
            primary_meals = engine.preference_recommendations(filters_used.limit)
            primary_reason = "根據你的偏好"
        elif action == "surprise":
            primary_meals = engine.random_meals((data or {}).get("limit") or filters_used.limit)
            primary_reason = "驚喜推薦"
        else:
            filter_form = RecommendationFilterForm(data=data, initial=initial_data)
            if filter_form.is_valid():
                filters_used = engine.filters_from_data(filter_form.cleaned_data)
                primary_meals = engine.apply_filters(filters_used)
                primary_reason = engine.describe_filters(filters_used)
            else:
                primary_meals = []
    else:
        primary_meals = engine.preference_recommendations(filters_used.limit)

    if not primary_meals:
        primary_meals = engine.popular_meals(filters_used.limit)
        recommendation_alert = "目前找不到符合條件的餐點，先為你帶來熱門選擇。"
        primary_reason = "熱門推薦"

    used_ids: set[int] = set()
    primary_cards = _build_recommendation_cards(primary_meals, primary_reason, used_ids)

    sections_config = [
        ("熱門收藏", "依收藏數排序", engine.popular_meals(4)),
        ("親民價位", "低價位也能享受美味", engine.budget_friendly(4)),
        ("素食推薦", "友善素食選擇", engine.vegetarian_spotlight(4)),
        ("清爽不辣", "適合想吃清淡的一天", engine.mild_flavor(4)),
        ("新的體驗", "你尚未收藏或評論過", engine.new_experiences(4)),
    ]
    secondary_sections = []
    for title, subtitle, meals in sections_config:
        cards = _build_recommendation_cards(meals, subtitle, used_ids)
        if cards:
            secondary_sections.append(
                {
                    "title": title,
                    "subtitle": subtitle,
                    "cards": cards,
                }
            )

    preference_snapshot = None
    if preference:
        parts = []
        if preference.cuisine_type:
            parts.append(preference.cuisine_type)
        if preference.category:
            parts.append(f"品項 {preference.category}")
        if preference.price_range:
            parts.append(f"價格 {preference.price_range}")
        if preference.is_vegetarian:
            parts.append("素食")
        if preference.avoid_spicy:
            parts.append("不辣")
        preference_snapshot = " · ".join(parts) if parts else "尚未設定明確條件"

    return {
        "filter_form": filter_form,
        "primary_recommendations": primary_cards,
        "primary_reason": primary_reason,
        "secondary_sections": secondary_sections,
        "recommendation_alert": recommendation_alert,
        "preference_snapshot": preference_snapshot,
        "cooldown_days": cooldown_days,
    }


@user_login_required
def home(request):
    user = get_current_user(request)
    today = timezone.now().date()
    today_stats = summarize_today(user, today)
    recent_meals = (
        DailyMealRecord.objects.filter(user=user)
        .order_by("-date", "-created_at")
        .select_related("user")[:4]
    )
    weekly_summary = recalculate_weekly_summary(user, today)
    ensure_notification_settings(user)
    notification_settings = NotificationSetting.objects.filter(user=user)
    upcoming = notification_settings.filter(is_enabled=True).order_by("scheduled_time")
    latest_notifications = NotificationLog.objects.filter(user=user).order_by("-sent_at")[:3]
    return _render(
        request,
        "usersideapp/home.html",
        "home",
        {
            "today_stats": today_stats,
            "today_date": today,
            "recent_meals": recent_meals,
            "weekly_summary": weekly_summary,
            "notification_settings": notification_settings,
            "next_reminder": upcoming.first() if upcoming else None,
            "latest_notifications": latest_notifications,
        },
    )


@user_login_required
def search_restaurants(request):
    form = RestaurantSearchForm(request.GET or None)
    cleaned_filters = {}
    if form.is_bound and form.is_valid():
        cleaned_filters = form.cleaned_data

    restaurants_qs = Restaurant.objects.filter(is_active=True)
    meals_qs = (
        Meal.objects.filter(is_available=True, restaurant__is_active=True)
        .select_related("restaurant")
    )
    keyword = cleaned_filters.get("keyword")
    if keyword:
        restaurants_qs = restaurants_qs.filter(
            Q(name__icontains=keyword)
            | Q(address__icontains=keyword)
            | Q(cuisine_type__icontains=keyword)
            | Q(meals__name__icontains=keyword)
            | Q(meals__description__icontains=keyword)
        ).distinct()
        meals_qs = meals_qs.filter(
            Q(name__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(restaurant__name__icontains=keyword)
        )
    city = cleaned_filters.get("city")
    if city:
        restaurants_qs = restaurants_qs.filter(city__icontains=city)
        meals_qs = meals_qs.filter(restaurant__city__icontains=city)
    district = cleaned_filters.get("district")
    if district:
        restaurants_qs = restaurants_qs.filter(district__icontains=district)
        meals_qs = meals_qs.filter(restaurant__district__icontains=district)
    cuisine_type = cleaned_filters.get("cuisine_type")
    if cuisine_type:
        restaurants_qs = restaurants_qs.filter(cuisine_type__icontains=cuisine_type)
        meals_qs = meals_qs.filter(restaurant__cuisine_type__icontains=cuisine_type)
    category = cleaned_filters.get("category")
    if category:
        restaurants_qs = restaurants_qs.filter(meals__category__iexact=category).distinct()
        meals_qs = meals_qs.filter(category__iexact=category)
    price_range = cleaned_filters.get("price_range")
    if price_range:
        restaurants_qs = restaurants_qs.filter(price_range=price_range)
        meals_qs = meals_qs.filter(restaurant__price_range=price_range)

    restaurants_qs = restaurants_qs.order_by("-rating", "name")
    total_results = restaurants_qs.count()
    restaurants = list(restaurants_qs[:MAX_MAP_RESULTS])
    limited = total_results > len(restaurants)

    meals_qs = meals_qs.order_by("name")
    meal_total_results = meals_qs.count()
    meals = list(meals_qs[:MAX_MEAL_RESULTS])
    meal_limited = meal_total_results > len(meals)

    user_location = None
    latitude = cleaned_filters.get("latitude")
    longitude = cleaned_filters.get("longitude")
    if latitude is not None and longitude is not None:
        user_location = (latitude, longitude)

    markers = []
    for restaurant in restaurants:
        if restaurant.latitude is None or restaurant.longitude is None:
            continue
        markers.append(
            {
                "name": restaurant.name,
                "lat": float(restaurant.latitude),
                "lon": float(restaurant.longitude),
                "address": restaurant.address or "",
                "cuisine": restaurant.cuisine_type or "",
                "price": restaurant.get_price_range_display(),
                "rating": restaurant.rating,
            }
        )

    center_lat, center_lon = DEFAULT_MAP_CENTER
    zoom_start = 13 if markers else 7
    if user_location:
        center_lat, center_lon = user_location
        zoom_start = 15
    elif markers:
        center_lat = sum(marker["lat"] for marker in markers) / len(markers)
        center_lon = sum(marker["lon"] for marker in markers) / len(markers)
    restaurant_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        control_scale=True,
        tiles="OpenStreetMap",
        width="100%",
        height="600px",
    )

    Fullscreen(position="topright", title="進入全螢幕", title_cancel="退出全螢幕").add_to(restaurant_map)
    LocateControl(
        auto_start=False,
        keepCurrentZoomLevel=True,
        flyTo=True,
        strings={"title": "移動到目前位置", "popup": "目前位置"},
    ).add_to(restaurant_map)

    bounds_points: list[list[float]] = []
    if user_location:
        folium.CircleMarker(
            location=user_location,
            radius=8,
            color="#2563eb",
            fill=True,
            fill_color="#2563eb",
            fill_opacity=0.9,
            tooltip="目前位置",
        ).add_to(restaurant_map)
        bounds_points.append([user_location[0], user_location[1]])

    if markers:
        bounds_points.extend([[marker["lat"], marker["lon"]] for marker in markers])
    if len(bounds_points) >= 2:
        restaurant_map.fit_bounds(bounds_points, padding=(20, 20))
    elif len(bounds_points) == 1:
        restaurant_map.location = bounds_points[0]
        restaurant_map.zoom_start = 15

    for marker in markers:
        popup_lines = [f"<strong>{escape(marker['name'])}</strong>"]
        if marker["address"]:
            popup_lines.append(escape(marker["address"]))
        detail_parts = []
        if marker["cuisine"]:
            detail_parts.append(escape(marker["cuisine"]))
        if marker["price"]:
            detail_parts.append(escape(marker["price"]))
        if marker["rating"] is not None:
            detail_parts.append(f"評分：{marker['rating']}")
        if detail_parts:
            popup_lines.append(" ・ ".join(detail_parts))
        popup_html = "<br/>".join(popup_lines)
        folium.Marker(
            [marker["lat"], marker["lon"]],
            tooltip=marker["name"],
            popup=folium.Popup(popup_html, max_width=280),
        ).add_to(restaurant_map)

    folium_map_html = restaurant_map._repr_html_()
    map_hint = None
    if not markers and not user_location:
        map_hint = "目前結果缺少座標資訊，顯示預設地圖。"
    elif not markers and user_location:
        map_hint = "已使用您的定位，但目前尚無提供座標的餐廳資料。"

    return _render(
        request,
        "usersideapp/search.html",
        "search",
        {
            "form": form,
            "restaurants": restaurants,
            "result_count": total_results,
            "limit_reached": limited,
            "meals": meals,
            "meal_result_count": meal_total_results,
            "meal_limit_reached": meal_limited,
            "folium_map": folium_map_html,
            "map_has_markers": bool(markers),
         	"has_user_location": bool(user_location),
         	"map_hint": map_hint,
        },
    )


@user_login_required
def random_recommendation(request):
    user = get_current_user(request)
    form_data = request.POST if request.method == "POST" else None
    context = _build_random_context(user, form_data)
    return _render(
        request,
        "usersideapp/random.html",
        "random",
        context,
    )


@require_POST
@user_login_required
def random_recommendation_data(request):
    user = get_current_user(request)
    context = _build_random_context(user, request.POST)
    data = {
        "primary": {
            "reason": context["primary_reason"],
            "cards": [_serialize_card(card) for card in context["primary_recommendations"]],
        },
        "secondary": [
            {
                "title": section["title"],
                "subtitle": section["subtitle"],
                "cards": [_serialize_card(card) for card in section["cards"]],
            }
            for section in context["secondary_sections"]
        ],
        "alert": context["recommendation_alert"],
        "preferenceSnapshot": context["preference_snapshot"],
        "formErrors": _collect_form_errors(context["filter_form"]),
        "cooldownDays": context["cooldown_days"],
    }
    return JsonResponse(data)


@user_login_required
def today_meal(request):
    user = get_current_user(request)
    today = timezone.now().date()
    stats = summarize_today(user, today)
    today_records = (
        DailyMealRecord.objects.filter(user=user, date=today)
        .prefetch_related("components")
        .order_by("meal_type")
    )
    records_by_type = {meal: None for meal in DailyMealRecord.MealType.values}
    for record in today_records:
        records_by_type[record.meal_type] = record
    meal_blocks = [
        {"value": value, "label": label, "record": records_by_type.get(value)}
        for value, label in DailyMealRecord.MealType.choices
    ]
    return _render(
        request,
        "usersideapp/today_meal.html",
        "today",
        {
            "today_stats": stats,
            "meal_blocks": meal_blocks,
            "today_date": today,
        },
    )


@user_login_required
def record_meal(request):
    user = get_current_user(request)
    today = timezone.now().date()
    meal_form = None
    components_seed = "[]"
    editing_record = None
    original_record_date = None

    if request.method == "POST":
        components_seed = request.POST.get("components_payload", "[]")
        intent = request.POST.get("intent", "create")
        if intent == "delete":
            record_id = request.POST.get("record_id")
            record = DailyMealRecord.objects.filter(user=user, pk=record_id).first()
            if not record:
                messages.error(request, "找不到指定的飲食紀錄。")
            else:
                reference_date = record.date
                record.delete()
                recalculate_weekly_summary(user, reference_date)
                messages.success(request, "已刪除飲食紀錄。")
            return redirect("usersideapp:record")

        if intent == "update":
            record_id = request.POST.get("record_id")
            editing_record = (
                DailyMealRecord.objects.filter(user=user, pk=record_id)
                .prefetch_related("components")
                .first()
            )
            if not editing_record:
                messages.error(request, "找不到要編輯的飲食紀錄。")
                return redirect("usersideapp:record")
            original_record_date = editing_record.date
            meal_form = MealRecordForm(user=user, data=request.POST, instance=editing_record)
        else:
            meal_form = MealRecordForm(user=user, data=request.POST)

        if meal_form.is_valid():
            record = meal_form.save()
            _save_components(record, meal_form.components)
            if record.source_meal_id:
                record_user_choice(user, record.source_meal)
            recalculate_weekly_summary(user, record.date)
            if editing_record and original_record_date and original_record_date != record.date:
                recalculate_weekly_summary(user, original_record_date)
            if editing_record:
                messages.success(request, "已更新飲食紀錄。")
            else:
                log_meal_record_notification(user, record)
                messages.success(request, "已成功記錄今日飲食！")
            return redirect("usersideapp:record")
        messages.error(request, "請修正表單錯誤後再試一次。")
    else:
        edit_id = request.GET.get("edit")
        if edit_id:
            editing_record = (
                DailyMealRecord.objects.filter(user=user, pk=edit_id)
                .prefetch_related("components")
                .first()
            )
            if not editing_record:
                messages.error(request, "找不到指定的飲食紀錄。")
                return redirect("usersideapp:record")
            meal_form = MealRecordForm(user=user, instance=editing_record)
            components_seed = _serialize_components(editing_record)
    if meal_form is None:
        meal_form = MealRecordForm(user=user, initial={"date": today})

    day_range = request.GET.get("range", "7")
    range_filters = [
        ("7", "最近 7 天"),
        ("30", "最近 30 天"),
        ("month", "本月"),
    ]
    filter_lookup = {value: label for value, label in range_filters}
    selected_range_value = day_range if day_range in filter_lookup else "7"

    if selected_range_value == "month":
        start_date = today.replace(day=1)
        logic_hint = "本月資料，自 1 日起累計"
        rolling_days = (today - start_date).days + 1
    else:
        rolling_days = int(selected_range_value)
        start_date = today - timedelta(days=rolling_days - 1)
        logic_hint = "包含今日的滾動區間"

    date_window_label = f"{start_date:%Y/%m/%d} – {today:%Y/%m/%d}"
    selected_range_meta = {
        "value": selected_range_value,
        "label": filter_lookup.get(selected_range_value, filter_lookup["7"]),
        "date_window": date_window_label,
        "days": rolling_days,
        "logic_hint": logic_hint,
    }
    history = (
        DailyMealRecord.objects.filter(user=user, date__gte=start_date)
        .prefetch_related("components")
        .select_related("source_meal__restaurant")
        .order_by("-date", "meal_type")
    )
    aggregate_raw = history.aggregate(
        total_calories=Sum("calories"),
        total_protein=Sum("protein_grams"),
        total_carbs=Sum("carb_grams"),
        total_fat=Sum("fat_grams"),
    )
    aggregate = {key: value or 0 for key, value in aggregate_raw.items()}
    if editing_record and request.method != "POST":
        components_seed = _serialize_components(editing_record)

    initial_restaurant_id = meal_form.initial.get("restaurant") or ""
    initial_meal_id = meal_form.initial.get("source_meal") or ""
    if editing_record and editing_record.source_meal_id:
        initial_meal_id = initial_meal_id or editing_record.source_meal_id
        if editing_record.source_meal:
            initial_restaurant_id = (
                initial_restaurant_id or editing_record.source_meal.restaurant_id
            )
    if meal_form and not meal_form.is_bound:
        meal_form.initial["components_payload"] = components_seed

    return _render(
        request,
        "usersideapp/record_meal.html",
        "record",
        {
            "meal_form": meal_form,
            "history_records": history,
            "history_totals": aggregate,
            "selected_range": selected_range_value,
            "range_filters": range_filters,
            "selected_range_meta": selected_range_meta,
            "components_seed": components_seed,
            "editing_record": editing_record,
            "initial_restaurant_id": initial_restaurant_id or "",
            "initial_meal_id": initial_meal_id or "",
        }
    )


@user_login_required
def restaurant_meals_api(request):
    restaurant_id = request.GET.get("restaurant_id")
    try:
        restaurant_id = int(restaurant_id)
    except (TypeError, ValueError):
        return JsonResponse({"meals": []})

    meals = (
        Meal.objects.filter(restaurant_id=restaurant_id, is_available=True)
        .select_related("nutrition")
        .order_by("name")
    )

    payload = []
    for meal in meals:
        nutrition = getattr(meal, "nutrition", None)
        nutrition_data = None
        if nutrition:
            nutrition_data = {
                "calories": str(nutrition.calories),
                "protein": str(nutrition.protein),
                "carbohydrate": str(nutrition.carbohydrate),
                "fat": str(nutrition.fat),
            }
        payload.append(
            {
                "id": meal.id,
                "name": meal.name,
                "nutrition": nutrition_data,
            }
        )

    return JsonResponse({"meals": payload})


@user_login_required
def notifications(request):
    user = get_current_user(request)
    ensure_notification_settings(user)
    queryset = NotificationSetting.objects.filter(user=user).order_by("reminder_type")
    formset = NotificationSettingFormSet(queryset=queryset)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_settings":
            formset = NotificationSettingFormSet(request.POST, queryset=queryset)
            if formset.is_valid():
                formset.save()
                messages.success(request, "提醒設定已更新。")
                return redirect("usersideapp:notify")
            messages.error(request, "提醒設定更新失敗，請確認欄位。")
        elif action == "mark_read":
            log_id = request.POST.get("log_id")
            updated = NotificationLog.objects.filter(user=user, pk=log_id).update(
                status=NotificationLog.Status.READ,
                read_at=timezone.now(),
            )
            if updated:
                messages.success(request, "通知已標記為已讀。")
            else:
                messages.error(request, "找不到該通知或已經處理。")
            return redirect("usersideapp:notify")
        elif action == "send_preview":
            reminder_type = request.POST.get(
                "reminder_type", NotificationSetting.ReminderType.RANDOM
            )
            NotificationLog.objects.create(
                user=user,
                title="提醒已安排",
                body=f"{reminder_type} 推播預覽",
                notification_type="preview",
            )
            messages.success(request, "已建立推播預覽通知。")
            return redirect("usersideapp:notify")

    logs = NotificationLog.objects.filter(user=user).order_by("-sent_at")[:10]
    return _render(
        request,
        "usersideapp/notify.html",
        "notify",
        {"formset": formset, "notification_logs": logs},
    )


@user_login_required
def health_advice(request):
    user = get_current_user(request)
    summary = build_health_summary(user)
    return _render(
        request,
        "usersideapp/health.html",
        "health",
        {"health_summary": summary},
    )


@user_login_required
def settings(request):
    user = get_current_user(request)
    preference, _ = UserPreference.objects.get_or_create(user=user)
    ensure_notification_settings(user)
    notifications = NotificationSetting.objects.filter(user=user).order_by("reminder_type")
    preference_form = UserPreferenceForm(user=user, instance=preference)
    account_form = AccountProfileForm(instance=user)
    password_form = PasswordChangeForm(user=user)
    if request.method == "POST":
        target = request.POST.get("form_type", "preferences")
        if target == "account":
            account_form = AccountProfileForm(data=request.POST, instance=user)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "帳戶資訊已更新。")
                return redirect("usersideapp:settings")
            messages.error(request, "帳戶資訊更新失敗，請檢查欄位。")
        elif target == "password":
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "密碼已更新，請重新使用新密碼登入。")
                return redirect("usersideapp:settings")
            messages.error(request, "密碼更新失敗，請檢查欄位。")
        else:
            preference_form = UserPreferenceForm(
                user=user,
                data=request.POST,
                instance=preference,
            )
            if preference_form.is_valid():
                preference_form.save()
                messages.success(request, "偏好設定已更新。")
                return redirect("usersideapp:settings")
            messages.error(request, "更新失敗，請檢查輸入欄位。")
    return _render(
        request,
        "usersideapp/settings.html",
        "settings",
        {
            "preference_form": preference_form,
            "account_form": account_form,
            "password_form": password_form,
            "notification_settings": notifications,
        },
    )


@user_login_required
def interactions(request):
    user = get_current_user(request)
    edit_review_id = request.GET.get("edit_review")
    editing_review = None
    if edit_review_id:
        editing_review = (
            Review.objects.filter(user=user, pk=edit_review_id)
            .select_related("restaurant", "meal")
            .first()
        )
        if not editing_review:
            messages.error(request, "找不到要編輯的評論。")
    review_form = ReviewForm(user=user, instance=editing_review)
    favorite_form = FavoriteForm(user=user)
    user_reviews = (
        Review.objects.filter(user=user)
        .select_related("restaurant", "meal", "meal__restaurant")
        .order_by("-created_at")
    )
    favorites = (
        Favorite.objects.filter(user=user)
        .select_related("meal", "meal__restaurant")
        .order_by("-created_at")
    )
    if request.method == "POST":
        action = request.POST.get("form_type")
        if action == "review":
            review_instance = None
            review_id = request.POST.get("review_id")
            if review_id:
                review_instance = Review.objects.filter(user=user, pk=review_id).first()
                if not review_instance:
                    messages.error(request, "無法編輯指定的評論。")
            review_form = ReviewForm(user=user, data=request.POST, instance=review_instance)
            if review_form.is_valid():
                meal = review_form.cleaned_data["meal"]
                duplicate_qs = Review.objects.filter(user=user, meal=meal)
                if review_instance:
                    duplicate_qs = duplicate_qs.exclude(pk=review_instance.pk)
                if duplicate_qs.exists():
                    review_form.add_error(
                        "meal",
                        "你已評論過此餐點，可直接編輯原評論。",
                    )
                else:
                    review_form.save()
                    if review_instance:
                        messages.success(request, "評論已更新。")
                    else:
                        messages.success(request, "感謝您的評論！")
                    return redirect("usersideapp:interactions")
            editing_review = review_instance or editing_review
            messages.error(request, "評論送出失敗，請檢查欄位。")
        elif action == "favorite_add":
            favorite_form = FavoriteForm(user=user, data=request.POST)
            if favorite_form.is_valid():
                favorite_form.save()
                messages.success(request, "已加入收藏餐點。")
                return redirect("usersideapp:interactions")
            messages.error(request, "收藏失敗，請重新選擇餐點。")
        elif action == "favorite_remove":
            favorite_id = request.POST.get("favorite_id")
            deleted, _ = Favorite.objects.filter(user=user, pk=favorite_id).delete()
            if deleted:
                messages.success(request, "已移除收藏餐點。")
            else:
                messages.error(request, "找不到要移除的收藏。")
            return redirect("usersideapp:interactions")
    return _render(
        request,
        "usersideapp/interactions.html",
        "interactions",
        {
            "review_form": review_form,
            "favorite_form": favorite_form,
            "user_reviews": user_reviews,
            "favorites": favorites,
            "editing_review": editing_review,
        },
    )
