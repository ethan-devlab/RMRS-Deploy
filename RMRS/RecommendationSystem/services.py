from __future__ import annotations

from datetime import timedelta
from typing import Iterable

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import RecommendationHistory


DEFAULT_COOLDOWN_DAYS = 7
MIN_COOLDOWN_DAYS = 1
MAX_COOLDOWN_DAYS = 30


def _sanitize_days(value: int | None, fallback: int = DEFAULT_COOLDOWN_DAYS) -> int:
    try:
        parsed = int(value) if value is not None else None
    except (TypeError, ValueError):
        parsed = None
    if parsed is None:
        return fallback
    return max(MIN_COOLDOWN_DAYS, min(MAX_COOLDOWN_DAYS, parsed))


def get_recommendation_cooldown_days(user=None) -> int:
    """Return cooldown in days, honoring user preference when available."""

    fallback = DEFAULT_COOLDOWN_DAYS
    if user is None:
        return fallback

    preference = None
    try:
        preference = getattr(user, "preferences", None)
    except ObjectDoesNotExist:
        preference = None

    user_value = getattr(preference, "recommendation_cooldown_days", None)
    if user_value is None:
        return fallback
    return _sanitize_days(user_value, fallback)


def record_user_choice(user, meal) -> RecommendationHistory | None:
    """Persist that a user actually selected a recommended meal."""
    if not getattr(user, "pk", None) or meal is None:
        return None
    restaurant = getattr(meal, "restaurant", None)
    return RecommendationHistory.objects.create(
        user=user,
        meal=meal,
        restaurant=restaurant,
        was_selected=True,
    )


def recent_selected_meal_ids(user, days: int | None = None) -> Iterable[int]:
    """Return a queryset of meal IDs the user selected within the window."""
    if not getattr(user, "pk", None):
        return RecommendationHistory.objects.none().values_list("meal_id", flat=True)
    window_days = max(1, days) if days is not None else get_recommendation_cooldown_days(user)
    cutoff = timezone.now() - timedelta(days=window_days)
    return (
        RecommendationHistory.objects.filter(
            user=user,
            was_selected=True,
            recommended_at__gte=cutoff,
        )
        .values_list("meal_id", flat=True)
        .distinct()
    )
