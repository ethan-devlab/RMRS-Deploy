"""Restaurant-related views for MerchantSideApp."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..auth_utils import get_current_merchant, merchant_login_required
from ..models import Restaurant


def restaurant_detail(request, restaurant_slug):
    """Display restaurant details (public view)."""
    merchant = get_current_merchant(request)
    restaurant = get_object_or_404(
        Restaurant.objects.prefetch_related("meals"),
        slug=restaurant_slug,
    )

    meals_qs = restaurant.meals.order_by("-updated_at", "-id")
    meals = list(meals_qs)
    total = len(meals)
    available = sum(1 for meal in meals if meal.is_available)
    stats = {
        "total_meals": total,
        "available_meals": available,
        "unavailable_meals": total - available,
        "last_updated": meals[0].updated_at if meals else None,
    }
    can_edit = bool(
        merchant
        and getattr(merchant, "restaurant_id", None) == restaurant.id
    )

    return render(
        request,
        "merchantsideapp/restaurant.html",
        {
            "restaurant": restaurant,
            "meals": meals,
            "stats": stats,
            "can_edit": can_edit,
        },
    )


@merchant_login_required
def update_restaurant_status(request):
    """Update the restaurant's open/closed status."""
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
