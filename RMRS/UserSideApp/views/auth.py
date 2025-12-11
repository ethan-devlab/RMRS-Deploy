from django.contrib import messages
from django.shortcuts import redirect, render

from ..auth_utils import get_current_user, login_user, logout_user
from ..forms import UserLoginForm, UserRegistrationForm

from django_ratelimit.decorators import ratelimit


@ratelimit(key="ip", rate="5/m", block=True)
def login_view(request):
    if get_current_user(request):
        messages.info(request, "您已登入。")
        return redirect("usersideapp:home")

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login_user(request, user)
            messages.success(request, f"歡迎回來，{user.username}！")
            return redirect("usersideapp:home")
    else:
        form = UserLoginForm()

    return render(request, "usersideapp/login.html", {"form": form})


@ratelimit(key="ip", rate="5/m", block=True)
def register_view(request):
    if get_current_user(request):
        messages.info(request, "您已登入。")
        return redirect("usersideapp:home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login_user(request, user)
            messages.success(request, "帳號建立成功，歡迎加入！")
            return redirect("usersideapp:home")
    else:
        form = UserRegistrationForm()

    return render(request, "usersideapp/register.html", {"form": form})


@ratelimit(key="ip", rate="5/m", block=True)
def logout_view(request):
    logout_user(request)
    messages.success(request, "您已成功登出。")
    return redirect("usersideapp:login")
