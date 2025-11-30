"""Home page view for UserSideApp."""

from django.utils import timezone

from ..auth_utils import get_current_user, user_login_required
from ..models import DailyMealRecord, NotificationLog, NotificationSetting
from ..services import (
    ensure_notification_settings,
    recalculate_weekly_summary,
    summarize_today,
)
from .utils import _render


@user_login_required
def home(request):
    """Display user's home dashboard."""
    user = get_current_user(request)
    today = timezone.now().date()
    today_stats = summarize_today(user, today)
    recent_meals = (
        DailyMealRecord.objects.filter(user=user)
        .order_by("-date", "-created_at")
        .select_related("user")[:4]
    )
    weekly_summary = recalculate_weekly_summary(user, today)
    ensure_notification_settings(user)
    notification_settings = NotificationSetting.objects.filter(user=user)
    upcoming = notification_settings.filter(is_enabled=True).order_by("scheduled_time")
    latest_notifications = NotificationLog.objects.filter(user=user).order_by("-sent_at")[:3]
    return _render(
        request,
        "usersideapp/home.html",
        "home",
        {
            "today_stats": today_stats,
            "today_date": today,
            "recent_meals": recent_meals,
            "weekly_summary": weekly_summary,
            "notification_settings": notification_settings,
            "next_reminder": upcoming.first() if upcoming else None,
            "latest_notifications": latest_notifications,
        },
    )
