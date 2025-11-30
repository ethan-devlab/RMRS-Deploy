"""Meal-related views for UserSideApp."""

from datetime import timedelta

from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone

from MerchantSideApp.models import Meal
from RecommendationSystem.services import record_user_choice

from ..auth_utils import get_current_user, user_login_required
from ..forms import MealRecordForm
from ..models import DailyMealRecord
from ..services import (
    log_meal_record_notification,
    recalculate_weekly_summary,
    summarize_today,
)
from .utils import _render, _save_components, _serialize_components


@user_login_required
def today_meal(request):
    """Display today's meal summary."""
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
    """Record or edit meal entries."""
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
    """API endpoint to get meals for a restaurant."""
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
