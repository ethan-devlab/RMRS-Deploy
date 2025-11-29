import json

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..auth_utils import get_current_merchant, merchant_login_required
from ..forms import (
    MealCreateForm,
    MerchantAccountForm,
    MerchantPasswordChangeForm,
    RestaurantProfileForm,
)
from UserSideApp.models import MealComponent


def _persist_nutrition_components(meal, entries):
    MealComponent.objects.filter(meal=meal).delete()
    if not entries:
        return
    MealComponent.objects.bulk_create(
        [
            MealComponent(
                meal=meal,
                name=entry["name"],
                quantity=entry["quantity"],
                calories=entry["calories"],
                metadata=entry["metadata"],
            )
            for entry in entries
        ],
    )


def _build_nutrition_payload(meal):
    entries = []
    for component in meal.nutrition_components.all().order_by("id"):
        metadata = component.metadata or {}
        entries.append(
            {
                "name": component.name,
                "quantity": component.quantity,
                "calories": float(component.calories),
                "protein": metadata.get("protein"),
                "carb": metadata.get("carb"),
                "fat": metadata.get("fat"),
                "notes": metadata.get("notes"),
            }
        )
    return json.dumps(entries, ensure_ascii=False)


@merchant_login_required
def dashboard(request):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    recent_meals = []
    today_count = 0
    last_updated_meal = None
    merchant_display_name = (merchant.display_name or "").strip() if merchant else ""
    if restaurant is not None:
        meals_qs = restaurant.meals.order_by("-updated_at", "-id")
        recent_meals = list(meals_qs[:3])
        today = timezone.now().date()
        today_count = restaurant.meals.filter(updated_at__date=today).count()
        last_updated_meal = meals_qs.first()
        if not merchant_display_name:
            merchant_display_name = restaurant.name or ""

    merchant_display_name = merchant_display_name or "老闆"

    return render(
        request,
        "merchantsideapp/dashboard.html",
        {
            "merchant": merchant,
            "restaurant": restaurant,
            "recent_meals": recent_meals,
            "today_count": today_count,
            "last_updated_meal": last_updated_meal,
            "status_slug": "open" if getattr(restaurant, "is_active", False) else "closed",
            "merchant_display_name": merchant_display_name,
        },
    )


@merchant_login_required
def add_meal(request):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    if request.method == "POST":
        form = MealCreateForm(restaurant, request.POST)
        if form.is_valid():
            with transaction.atomic():
                meal = form.save()
                entries = getattr(form, "nutrition_entries", [])
                _persist_nutrition_components(meal, entries)
            messages.success(request, "餐點已建立，歡迎前往管理列表查看。")
            return redirect("merchantsideapp:manage_meals")
    else:
        form = MealCreateForm(restaurant)

    return render(
        request,
        "merchantsideapp/add_meal.html",
        {"form": form, "restaurant": restaurant, "page_title": "新增餐點"},
    )


@merchant_login_required
def manage_meals(request):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    meals = restaurant.meals.annotate(nutrition_count=Count("nutrition_components"))
    keyword = request.GET.get("keyword", "").strip()
    category_filter = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if keyword:
        meals = meals.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
    if category_filter:
        meals = meals.filter(category__iexact=category_filter)
    if status_filter == "available":
        meals = meals.filter(is_available=True)
    elif status_filter == "unavailable":
        meals = meals.filter(is_available=False)

    meals = meals.order_by("-updated_at", "-id").prefetch_related("nutrition_components")
    archived_preview = list(
        restaurant.meals.filter(is_available=False)
        .order_by("-updated_at", "-id")
        .prefetch_related("nutrition_components")[:5]
    )
    categories = (
        restaurant.meals.exclude(category__isnull=True)
        .exclude(category__exact="")
        .values_list("category", flat=True)
        .order_by("category")
        .distinct()
    )

    return render(
        request,
        "merchantsideapp/manage_meals.html",
        {
            "restaurant": restaurant,
            "meals": meals,
            "categories": categories,
            "keyword": keyword,
            "selected_category": category_filter,
            "selected_status": status_filter,
            "archived_preview": archived_preview,
        },
    )


@merchant_login_required
def edit_meal(request, meal_id):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    meal = get_object_or_404(
        restaurant.meals.prefetch_related("nutrition_components"), pk=meal_id
    )

    if request.method == "POST":
        form = MealCreateForm(restaurant, request.POST, instance=meal)
        if form.is_valid():
            with transaction.atomic():
                updated_meal = form.save()
                _persist_nutrition_components(
                    updated_meal,
                    getattr(form, "nutrition_entries", []),
                )
            messages.success(request, "餐點資訊已更新。")
            return redirect("merchantsideapp:manage_meals")
    else:
        payload = _build_nutrition_payload(meal)
        form = MealCreateForm(
            restaurant,
            instance=meal,
            initial={"nutrition_payload": payload},
        )
        form.fields["nutrition_payload"].initial = payload

    return render(
        request,
        "merchantsideapp/add_meal.html",
        {
            "form": form,
            "restaurant": restaurant,
            "meal": meal,
            "is_edit": True,
            "page_title": "編輯餐點",
        },
    )


@merchant_login_required
def delete_meal(request, meal_id):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    meal = get_object_or_404(restaurant.meals, pk=meal_id)
    if request.method != "POST":
        messages.warning(request, "請使用下架按鈕完成操作。")
        return redirect("merchantsideapp:manage_meals")

    if not meal.is_available:
        messages.info(request, f"「{meal.name}」已經是下架狀態。")
        return redirect("merchantsideapp:manage_meals")

    meal.is_available = False
    meal.updated_at = timezone.now()
    meal.save(update_fields=["is_available", "updated_at"])
    messages.success(
        request,
        f"已將「{meal.name}」移至已下架清單，可於需要時再次編輯上架。",
    )
    return redirect("merchantsideapp:manage_meals")


@merchant_login_required
def settings(request):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    account_form = MerchantAccountForm(instance=merchant)
    password_form = MerchantPasswordChangeForm(merchant=merchant)
    restaurant_form = RestaurantProfileForm(instance=restaurant)

    if request.method == "POST":
        target = request.POST.get("form_type", "restaurant")
        if target == "account":
            account_form = MerchantAccountForm(request.POST, instance=merchant)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "帳戶資訊已更新。")
                return redirect("merchantsideapp:settings")
            messages.error(request, "帳戶資訊更新失敗，請檢查欄位。")
        elif target == "password":
            password_form = MerchantPasswordChangeForm(merchant=merchant, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "密碼已更新，請使用新密碼重新登入。")
                return redirect("merchantsideapp:settings")
            messages.error(request, "密碼更新失敗，請檢查欄位。")
        else:
            if restaurant is None:
                messages.error(request, "找不到對應的餐廳資訊。")
            else:
                restaurant_form = RestaurantProfileForm(request.POST, instance=restaurant)
                if restaurant_form.is_valid():
                    restaurant_form.save()
                    messages.success(request, "餐廳資訊已更新。")
                    return redirect("merchantsideapp:settings")
                messages.error(request, "餐廳資訊更新失敗，請檢查欄位。")

    return render(
        request,
        "merchantsideapp/settings.html",
        {
            "merchant": merchant,
            "restaurant": restaurant,
            "account_form": account_form,
            "password_form": password_form,
            "restaurant_form": restaurant_form,
        },
    )


@merchant_login_required
def update_restaurant_status(request):
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    if request.method != "POST":
        return redirect("merchantsideapp:dashboard")

    status = request.POST.get("status")
    if status not in {"open", "closed"}:
        messages.warning(request, "請選擇有效的營業狀態。")
        return redirect("merchantsideapp:dashboard")

    is_active = status == "open"
    if restaurant.is_active != is_active:
        restaurant.is_active = is_active
        restaurant.save(update_fields=["is_active", "updated_at"])
        messages.success(
            request,
            "已將餐廳狀態更新為{}。".format("可接單" if is_active else "暫停接單"),
        )
    else:
        messages.info(request, "餐廳狀態未變更。")
    return redirect("merchantsideapp:dashboard")
