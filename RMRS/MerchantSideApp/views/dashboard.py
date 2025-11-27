from django.shortcuts import render

from ..auth_utils import get_current_merchant, merchant_login_required


@merchant_login_required
def dashboard(request):
    merchant = get_current_merchant(request)
    return render(
        request,
        "merchantsideapp/dashboard.html",
        {"merchant": merchant, "restaurant": getattr(merchant, "restaurant", None)},
    )


@merchant_login_required
def add_meal(request):
    return render(request, "merchantsideapp/add_meal.html")


@merchant_login_required
def manage_meals(request):
    return render(request, "merchantsideapp/manage_meals.html")
