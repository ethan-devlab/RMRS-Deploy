"""Health advice view for UserSideApp."""

from ..auth_utils import get_current_user, user_login_required
from ..services import build_health_summary
from .utils import _render


@user_login_required
def health_advice(request):
    """Display health advice and summary."""
    user = get_current_user(request)
    summary = build_health_summary(user)
    return _render(
        request,
        "usersideapp/health.html",
        "health",
        {"health_summary": summary},
    )
