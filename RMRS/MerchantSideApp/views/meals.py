"""Meal management views for MerchantSideApp."""

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..auth_utils import get_current_merchant, merchant_login_required
from ..forms import MealCreateForm
from ..models import Meal
from .utils import (
    _build_display_nutrition,
    _build_nutrition_payload,
    _extract_ingredients,
    _persist_nutrition_components,
)


@merchant_login_required
def add_meal(request):
    """Add a new meal to the restaurant menu."""
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    if request.method == "POST":
        form = MealCreateForm(restaurant, request.POST, request.FILES)
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
    """List and manage all meals for the restaurant."""
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


def meal_detail(request, meal_id):
    """Display meal details (public view)."""
    merchant = get_current_merchant(request)
    meal = get_object_or_404(
        Meal.objects.select_related("restaurant", "nutrition").prefetch_related("nutrition_components"),
        pk=meal_id,
    )
    restaurant = meal.restaurant
    nutrition = _build_display_nutrition(meal)
    components = list(meal.nutrition_components.order_by("id"))
    ingredients, allergens = _extract_ingredients(components)
    stock_status = "庫存充足" if meal.is_available else "暫停供應"
    setattr(meal, "stock_status", stock_status)
    can_edit = bool(
        merchant
        and getattr(merchant, "restaurant_id", None) == restaurant.id
    )
    image_source = meal.get_image_source()

    return render(
        request,
        "merchantsideapp/meal.html",
        {
            "meal": meal,
            "restaurant": restaurant,
            "nutrition": nutrition,
            "ingredients": ingredients,
            "allergens": allergens,
            "can_edit": can_edit,
            "image_source": image_source,
        },
    )


@merchant_login_required
def edit_meal(request, meal_id):
    """Edit an existing meal."""
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    meal = get_object_or_404(
        restaurant.meals.prefetch_related("nutrition_components"), pk=meal_id
    )

    if request.method == "POST":
        form = MealCreateForm(restaurant, request.POST, request.FILES, instance=meal)
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
    """Activate or deactivate a meal."""
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    if restaurant is None:
        messages.error(request, "無法識別您的商家資訊，請重新登入。")
        return redirect("merchantsideapp:login")

    meal = get_object_or_404(restaurant.meals, pk=meal_id)
    if request.method != "POST":
        messages.warning(request, "請使用狀態切換按鈕完成操作。")
        return redirect("merchantsideapp:manage_meals")

    action = request.POST.get("action", "deactivate")
    if action not in {"activate", "deactivate"}:
        messages.error(request, "無法判斷欲更新的餐點狀態。")
        return redirect("merchantsideapp:manage_meals")

    desired_state = action == "activate"
    if meal.is_available == desired_state:
        state_label = "上架" if desired_state else "下架"
        messages.info(request, f"「{meal.name}」已經是{state_label}狀態。")
        return redirect("merchantsideapp:manage_meals")

    meal.is_available = desired_state
    meal.updated_at = timezone.now()
    meal.save(update_fields=["is_available", "updated_at"])

    if desired_state:
        messages.success(request, f"已重新上架「{meal.name}」，立即回到菜單中。")
    else:
        messages.success(
            request,
            f"已將「{meal.name}」移至已下架清單，可於需要時再次編輯上架。",
        )
    return redirect("merchantsideapp:manage_meals")
