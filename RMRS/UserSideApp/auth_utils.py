from functools import wraps
from typing import Callable, Optional, TypeVar

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import AppUser

SESSION_USER_KEY = "app_user_id"
ViewFunc = TypeVar("ViewFunc", bound=Callable[..., HttpResponse])


def login_user(request: HttpRequest, user: AppUser) -> None:
    request.session[SESSION_USER_KEY] = user.pk
    request.session.modified = True


def logout_user(request: HttpRequest) -> None:
    if SESSION_USER_KEY in request.session:
        del request.session[SESSION_USER_KEY]
        request.session.modified = True


def get_current_user(request: HttpRequest) -> Optional[AppUser]:
    user_id = request.session.get(SESSION_USER_KEY)
    if not user_id:
        return None
    return AppUser.objects.filter(pk=user_id).first()


def user_login_required(view_func: ViewFunc) -> ViewFunc:
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not request.session.get(SESSION_USER_KEY):
            messages.info(request, "請先登入以存取該頁面。")
            return redirect("usersideapp:login")
        return view_func(request, *args, **kwargs)

    return _wrapped  # type: ignore[return-value]
