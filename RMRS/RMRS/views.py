"""Standalone views for project-level pages (e.g., error handlers)."""

from __future__ import annotations

from typing import Iterable, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


SITE_NAME = "Foodie"


def _render_error(
    request: HttpRequest,
    *,
    status_code: int,
    title: str,
    message: str,
    suggestions: Optional[Iterable[str]] = None,
) -> HttpResponse:
    """Render a shared error template with consistent context."""

    context = {
        "site_name": SITE_NAME,
        "error_code": status_code,
        "error_title": title,
        "error_message": message,
        "suggestions": list(suggestions or ()),
        "request_path": getattr(request, "path", ""),
        "is_debug": settings.DEBUG,
    }
    template_name = f"errors/{status_code}.html"
    return render(request, template_name, context=context, status=status_code)


def error_400(request: HttpRequest, exception: Exception) -> HttpResponse:
    return _render_error(
        request,
        status_code=400,
        title="無法處理的請求",
        message="伺服器無法理解目前的請求，請重新整理或返回上一頁再試一次。",
        suggestions=(
            "確認表單欄位或查詢參數格式是否正確",
            "重新整理頁面後再提交資料",
        ),
    )


def error_403(request: HttpRequest, exception: Exception) -> HttpResponse:
    return _render_error(
        request,
        status_code=403,
        title="沒有權限",
        message="您沒有存取此資源的權限，若需要進一步協助請聯絡系統管理員。",
        suggestions=(
            "檢查是否已登入正確的帳號",
            "確認帳號是否擁有相對應的操作權限",
        ),
    )


def error_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    return _render_error(
        request,
        status_code=404,
        title="找不到頁面",
        message="您造訪的頁面可能已被移除或更名，請回到首頁或使用搜尋功能。",
        suggestions=(
            "確認網址是否輸入正確",
            "使用搜尋功能尋找餐廳或餐點",
            "回到首頁重新操作",
        ),
    )


def error_500(request: HttpRequest) -> HttpResponse:
    return _render_error(
        request,
        status_code=500,
        title="系統忙線中",
        message="我們正在努力修復問題，請稍後再試或回報給系統管理員。",
        suggestions=(
            "稍後重新整理頁面",
            "若持續發生，請截圖並回報給支援人員",
        ),
    )
