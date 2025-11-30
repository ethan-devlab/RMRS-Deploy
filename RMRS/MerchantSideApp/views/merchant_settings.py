"""Merchant settings view for MerchantSideApp."""

from django.contrib import messages
from django.shortcuts import redirect, render

from ..auth_utils import get_current_merchant, merchant_login_required
from ..forms import (
    MerchantAccountForm,
    MerchantPasswordChangeForm,
    RestaurantNameForm,
    RestaurantProfileForm,
)


@merchant_login_required
def settings(request):
    """Manage merchant account and restaurant settings."""
    merchant = get_current_merchant(request)
    restaurant = getattr(merchant, "restaurant", None)
    account_form = MerchantAccountForm(instance=merchant)
    password_form = MerchantPasswordChangeForm(merchant=merchant)
    restaurant_form = RestaurantProfileForm(instance=restaurant)
    restaurant_name_form = RestaurantNameForm(instance=restaurant)

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
        elif target == "restaurant_name":
            if restaurant is None:
                messages.error(request, "找不到對應的餐廳資訊。")
            else:
                restaurant_name_form = RestaurantNameForm(request.POST, instance=restaurant)
                if restaurant_name_form.is_valid():
                    restaurant_name_form.save()
                    messages.success(request, "餐廳名稱已更新。")
                    return redirect("merchantsideapp:settings")
                messages.error(request, "餐廳名稱更新失敗，請檢查欄位。")
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
            "restaurant_name_form": restaurant_name_form,
        },
    )
