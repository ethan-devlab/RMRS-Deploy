from django.contrib import messages
from django.shortcuts import redirect, render

from ..auth_utils import get_current_merchant, login_merchant, logout_merchant
from ..forms import MerchantLoginForm, MerchantRegistrationForm


def login_view(request):
    if get_current_merchant(request):
        messages.info(request, "您已登入商家帳號。")
        return redirect("merchantsideapp:dashboard")

    if request.method == "POST":
        form = MerchantLoginForm(request.POST)
        if form.is_valid():
            merchant = form.get_merchant()
            if merchant:
                login_merchant(request, merchant)
                messages.success(request, "登入成功，歡迎回來！")
                return redirect("merchantsideapp:dashboard")
    else:
        form = MerchantLoginForm()

    return render(request, "merchantsideapp/login.html", {"form": form})


def register_view(request):
    if get_current_merchant(request):
        messages.info(request, "您已登入商家帳號。")
        return redirect("merchantsideapp:dashboard")

    if request.method == "POST":
        form = MerchantRegistrationForm(request.POST)
        if form.is_valid():
            merchant = form.save()
            login_merchant(request, merchant)
            messages.success(request, "帳號建立成功，歡迎加入 Foodie！")
            return redirect("merchantsideapp:dashboard")
    else:
        form = MerchantRegistrationForm()

    return render(request, "merchantsideapp/register.html", {"form": form})


def logout_view(request):
    logout_merchant(request)
    messages.success(request, "您已成功登出商家帳號。")
    return redirect("merchantsideapp:login")
