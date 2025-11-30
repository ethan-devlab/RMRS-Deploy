"""Dashboard view for MerchantSideApp."""

from django.shortcuts import render
from django.utils import timezone

from ..auth_utils import get_current_merchant, merchant_login_required


@merchant_login_required
def dashboard(request):
    """Display merchant dashboard."""
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    recent_meals = []
    today_count = 0
    last_updated_meal = None
    available_meals_count = 0
    total_meals_count = 0
    merchant_display_name = (merchant.merchant_name or "").strip() if merchant else ""
    if restaurant is not None:
        meals_qs = restaurant.meals.order_by("-updated_at", "-id")
        recent_meals = list(meals_qs[:3])
        today = timezone.now().date()
        today_count = restaurant.meals.filter(updated_at__date=today).count()
        last_updated_meal = meals_qs.first()
        total_meals_count = restaurant.meals.count()
        available_meals_count = restaurant.meals.filter(is_available=True).count()
        if not merchant_display_name:
            merchant_display_name = restaurant.name or ""

    merchant_display_name = merchant_display_name or "老闆"
    status_slug = "open" if getattr(restaurant, "is_active", False) else "closed"

    return render(
        request,
        "merchantsideapp/dashboard.html",
        {
            "merchant": merchant,
            "restaurant": restaurant,
            "recent_meals": recent_meals,
            "today_count": today_count,
            "last_updated_meal": last_updated_meal,
            "status_slug": status_slug,
            "merchant_display_name": merchant_display_name,
            "available_meals_count": available_meals_count,
            "total_meals_count": total_meals_count,
        },
    )
