from functools import wraps
from typing import Callable, Optional, TypeVar

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import MerchantAccount

SESSION_MERCHANT_KEY = "merchant_account_id"
ViewFunc = TypeVar("ViewFunc", bound=Callable[..., HttpResponse])


def login_merchant(request: HttpRequest, merchant: MerchantAccount) -> None:
    request.session[SESSION_MERCHANT_KEY] = merchant.pk
    request.session.modified = True
    request.session.set_expiry(0)  # Session expires on browser close


def logout_merchant(request: HttpRequest) -> None:
    if SESSION_MERCHANT_KEY in request.session:
        del request.session[SESSION_MERCHANT_KEY]
        request.session.modified = True


def get_current_merchant(request: HttpRequest) -> Optional[MerchantAccount]:
    merchant_id = request.session.get(SESSION_MERCHANT_KEY)
    if not merchant_id:
        return None
    return MerchantAccount.objects.select_related("restaurant").filter(pk=merchant_id).first()


def merchant_login_required(view_func: ViewFunc) -> ViewFunc:
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not request.session.get(SESSION_MERCHANT_KEY):
            messages.info(request, "請先登入商家帳號。")
            return redirect("merchantsideapp:login")
        return view_func(request, *args, **kwargs)

    return _wrapped  # type: ignore[return-value]
