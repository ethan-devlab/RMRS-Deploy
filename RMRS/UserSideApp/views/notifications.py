"""Notification views for UserSideApp."""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from ..auth_utils import get_current_user, user_login_required
from ..forms import NotificationSettingFormSet
from ..models import NotificationLog, NotificationSetting
from ..services import ensure_notification_settings
from .utils import _render


@user_login_required
def notifications(request):
    """Manage notification settings and view logs."""
    user = get_current_user(request)
    ensure_notification_settings(user)
    queryset = NotificationSetting.objects.filter(user=user).order_by("reminder_type")
    formset = NotificationSettingFormSet(queryset=queryset)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_settings":
            formset = NotificationSettingFormSet(request.POST, queryset=queryset)
            if formset.is_valid():
                formset.save()
                messages.success(request, "提醒設定已更新。")
                return redirect("usersideapp:notify")
            messages.error(request, "提醒設定更新失敗，請確認欄位。")
        elif action == "mark_read":
            log_id = request.POST.get("log_id")
            updated = NotificationLog.objects.filter(user=user, pk=log_id).update(
                status=NotificationLog.Status.READ,
                read_at=timezone.now(),
            )
            if updated:
                messages.success(request, "通知已標記為已讀。")
            else:
                messages.error(request, "找不到該通知或已經處理。")
            return redirect("usersideapp:notify")
        elif action == "send_preview":
            reminder_type = request.POST.get(
                "reminder_type", NotificationSetting.ReminderType.RANDOM
            )
            NotificationLog.objects.create(
                user=user,
                title="提醒已安排",
                body=f"{reminder_type} 推播預覽",
                notification_type="preview",
            )
            messages.success(request, "已建立推播預覽通知。")
            return redirect("usersideapp:notify")

    logs = NotificationLog.objects.filter(user=user).order_by("-sent_at")[:10]
    return _render(
        request,
        "usersideapp/notify.html",
        "notify",
        {"formset": formset, "notification_logs": logs},
    )
