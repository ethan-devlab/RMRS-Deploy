"""User settings view for UserSideApp."""

from django.contrib import messages
from django.shortcuts import redirect

from ..auth_utils import get_current_user, user_login_required
from ..forms import AccountProfileForm, PasswordChangeForm, UserPreferenceForm
from ..models import NotificationSetting, UserPreference
from ..services import ensure_notification_settings
from .utils import _render


@user_login_required
def settings(request):
    """Manage user preferences and account settings."""
    user = get_current_user(request)
    preference, _ = UserPreference.objects.get_or_create(user=user)
    ensure_notification_settings(user)
    notifications = NotificationSetting.objects.filter(user=user).order_by("reminder_type")
    preference_form = UserPreferenceForm(user=user, instance=preference)
    account_form = AccountProfileForm(instance=user)
    password_form = PasswordChangeForm(user=user)
    if request.method == "POST":
        target = request.POST.get("form_type", "preferences")
        if target == "account":
            account_form = AccountProfileForm(data=request.POST, instance=user)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "帳戶資訊已更新。")
                return redirect("usersideapp:settings")
            messages.error(request, "帳戶資訊更新失敗，請檢查欄位。")
        elif target == "password":
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "密碼已更新，請重新使用新密碼登入。")
                return redirect("usersideapp:settings")
            messages.error(request, "密碼更新失敗，請檢查欄位。")
        else:
            preference_form = UserPreferenceForm(
                user=user,
                data=request.POST,
                instance=preference,
            )
            if preference_form.is_valid():
                preference_form.save()
                messages.success(request, "偏好設定已更新。")
                return redirect("usersideapp:settings")
            messages.error(request, "更新失敗，請檢查輸入欄位。")
    return _render(
        request,
        "usersideapp/settings.html",
        "settings",
        {
            "preference_form": preference_form,
            "account_form": account_form,
            "password_form": password_form,
            "notification_settings": notifications,
        },
    )
