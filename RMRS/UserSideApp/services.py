from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta
from typing import Dict, List, Optional, Tuple

from django.db.models import Count, Q, Sum
from django.utils import timezone

from MerchantSideApp.models import Meal, Restaurant

from .models import (
    AppUser,
    DailyMealRecord,
    Favorite,
    NotificationLog,
    NotificationSetting,
    Review,
    UserPreference,
    WeeklyIntakeSummary,
)


@dataclass
class TodayMealStats:
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    by_meal_type: Dict[str, Dict[str, float]]


def get_week_bounds(target_date: date) -> Tuple[date, date]:
    """Return the Monday-start boundaries (start inclusive, end exclusive)."""
    start = target_date - timedelta(days=target_date.weekday())
    end = start + timedelta(days=7)
    return start, end


def recalculate_weekly_summary(user: AppUser, reference_date: Optional[date] = None) -> WeeklyIntakeSummary:
    """Rebuild the weekly intake summary for the week containing reference_date."""
    reference_date = reference_date or timezone.now().date()
    week_start, week_end = get_week_bounds(reference_date)
    qs = DailyMealRecord.objects.filter(
        user=user,
        date__gte=week_start,
        date__lt=week_end,
    )
    aggregates = qs.aggregate(
        total_calories=Sum("calories"),
        total_protein=Sum("protein_grams"),
        total_carbs=Sum("carb_grams"),
        total_fat=Sum("fat_grams"),
    )
    summary, _ = WeeklyIntakeSummary.objects.get_or_create(
        user=user,
        week_start=week_start,
        defaults={
            "total_calories": aggregates["total_calories"] or 0,
            "total_protein": aggregates["total_protein"] or 0,
            "total_carbs": aggregates["total_carbs"] or 0,
            "total_fat": aggregates["total_fat"] or 0,
            "meal_count": qs.count(),
        },
    )
    summary.total_calories = aggregates["total_calories"] or 0
    summary.total_protein = aggregates["total_protein"] or 0
    summary.total_carbs = aggregates["total_carbs"] or 0
    summary.total_fat = aggregates["total_fat"] or 0
    summary.meal_count = qs.count()
    summary.save(update_fields=[
        "total_calories",
        "total_protein",
        "total_carbs",
        "total_fat",
        "meal_count",
    ])
    return summary


def summarize_today(user: AppUser, target_date: Optional[date] = None) -> TodayMealStats:
    target_date = target_date or timezone.now().date()
    qs = DailyMealRecord.objects.filter(user=user, date=target_date)
    totals = qs.aggregate(
        total_calories=Sum("calories"),
        total_protein=Sum("protein_grams"),
        total_carbs=Sum("carb_grams"),
        total_fat=Sum("fat_grams"),
    )
    per_type: Dict[str, Dict[str, float]] = {}
    for record in qs:
        stats = per_type.setdefault(record.meal_type, {
            "calories": 0,
            "protein": 0,
        })
        stats["calories"] += float(record.calories)
        stats["protein"] += float(record.protein_grams)
    return TodayMealStats(
        total_calories=float(totals["total_calories"] or 0),
        total_protein=float(totals["total_protein"] or 0),
        total_carbs=float(totals["total_carbs"] or 0),
        total_fat=float(totals["total_fat"] or 0),
        by_meal_type=per_type,
    )


def ensure_notification_settings(user: AppUser) -> List[NotificationSetting]:
    """Guarantee that the user has baseline reminder rows for each meal."""
    defaults: List[Tuple[str, Optional[time]]] = [
        (NotificationSetting.ReminderType.BREAKFAST, time(hour=8, minute=0)),
        (NotificationSetting.ReminderType.LUNCH, time(hour=12, minute=30)),
        (NotificationSetting.ReminderType.DINNER, time(hour=18, minute=30)),
        (NotificationSetting.ReminderType.SNACK, time(hour=15, minute=30)),
        (NotificationSetting.ReminderType.RANDOM, None),
    ]
    settings: List[NotificationSetting] = []
    for reminder_type, scheduled_time in defaults:
        setting, _ = NotificationSetting.objects.get_or_create(
            user=user,
            reminder_type=reminder_type,
            defaults={
                "scheduled_time": scheduled_time,
                "is_enabled": True,
            },
        )
        settings.append(setting)
    return settings


def schedule_preview(setting: NotificationSetting) -> str:
    if not setting.is_enabled:
        return "已關閉"
    if setting.reminder_type == NotificationSetting.ReminderType.RANDOM:
        return "智慧推送"
    if setting.scheduled_time:
        return setting.scheduled_time.strftime("%H:%M")
    return "未設定"


def log_meal_record_notification(user: AppUser, record: DailyMealRecord) -> NotificationLog:
    """Create a progress notification after successfully logging a meal."""
    title = f"已記錄 {record.get_meal_type_display()}"
    body = f"{record.meal_name} · {record.calories} kcal"
    return NotificationLog.objects.create(
        user=user,
        title=title,
        body=body,
        notification_type="meal_record",
        status=NotificationLog.Status.SENT,
        extra_payload={
            "meal_type": record.meal_type,
            "record_id": record.pk,
        },
    )


@dataclass
class RecommendationFilters:
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    is_vegetarian: bool = False
    avoid_spicy: bool = False
    limit: int = 6


class RecommendationEngine:
    """High-level helper inspired by the CLI RecommendationEngine."""

    DEFAULT_LIMIT = 6

    def __init__(self, user: Optional[AppUser] = None):
        self.user = user

    def _base_queryset(self):
        return (
            Meal.objects.filter(is_available=True, restaurant__is_active=True)
            .select_related("restaurant")
            .annotate(favorite_count=Count("favorited_by"))
        )

    def _ensure_limit(self, limit: Optional[object]) -> int:
        try:
            value = int(limit) if limit is not None else self.DEFAULT_LIMIT
        except (TypeError, ValueError):
            value = self.DEFAULT_LIMIT
        return max(1, min(12, value))

    def initial_data(self, preference: Optional[UserPreference] = None) -> Dict[str, object]:
        pref = preference or getattr(self.user, "preferences", None)
        return {
            "cuisine_type": (pref.cuisine_type if pref and pref.cuisine_type else ""),
            "price_range": pref.price_range if pref and pref.price_range else "",
            "is_vegetarian": bool(pref.is_vegetarian) if pref else False,
            "avoid_spicy": bool(pref.avoid_spicy) if pref else False,
            "city": "",
            "district": "",
            "limit": self.DEFAULT_LIMIT,
        }

    def filters_from_data(self, data: Dict[str, object], limit: Optional[int] = None) -> RecommendationFilters:
        return RecommendationFilters(
            cuisine_type=str(data.get("cuisine_type") or "").strip() or None,
            price_range=data.get("price_range") or None,
            city=str(data.get("city") or "").strip() or None,
            district=str(data.get("district") or "").strip() or None,
            is_vegetarian=bool(data.get("is_vegetarian")),
            avoid_spicy=bool(data.get("avoid_spicy")),
            limit=self._ensure_limit(limit or data.get("limit")),
        )

    def filters_from_preferences(
        self,
        preference: Optional[UserPreference],
        limit: Optional[int] = None,
    ) -> RecommendationFilters:
        if not preference:
            return RecommendationFilters(limit=self._ensure_limit(limit))
        return RecommendationFilters(
            cuisine_type=preference.cuisine_type or None,
            price_range=preference.price_range or None,
            is_vegetarian=preference.is_vegetarian,
            avoid_spicy=preference.avoid_spicy,
            limit=self._ensure_limit(limit),
        )

    def apply_filters(self, filters: RecommendationFilters) -> List[Meal]:
        qs = self._base_queryset()
        if filters.cuisine_type:
            qs = qs.filter(restaurant__cuisine_type__icontains=filters.cuisine_type)
        if filters.price_range:
            qs = qs.filter(restaurant__price_range=filters.price_range)
        if filters.city:
            qs = qs.filter(restaurant__city__icontains=filters.city)
        if filters.district:
            qs = qs.filter(restaurant__district__icontains=filters.district)
        if filters.is_vegetarian:
            qs = qs.filter(is_vegetarian=True)
        if filters.avoid_spicy:
            qs = qs.filter(Q(is_spicy=False) | Q(is_spicy__isnull=True))
        return list(qs.order_by("-restaurant__rating", "name")[: filters.limit])

    def preference_recommendations(self, limit: Optional[int] = None) -> List[Meal]:
        preference = getattr(self.user, "preferences", None)
        filters = self.filters_from_preferences(preference, limit)
        results = self.apply_filters(filters)
        if results:
            return results
        return self.random_meals(filters.limit)

    def random_meals(self, limit: Optional[int] = None) -> List[Meal]:
        return list(
            self._base_queryset()
            .order_by("-restaurant__rating", "-created_at")
            [: self._ensure_limit(limit)]
        )

    def popular_meals(self, limit: Optional[int] = None) -> List[Meal]:
        return list(
            self._base_queryset()
            .order_by("-favorite_count", "-restaurant__rating", "name")
            [: self._ensure_limit(limit)]
        )

    def budget_friendly(self, limit: Optional[int] = None) -> List[Meal]:
        return list(
            self._base_queryset()
            .filter(restaurant__price_range=Restaurant.PriceRange.LOW)
            .order_by("-restaurant__rating", "name")[: self._ensure_limit(limit)]
        )

    def vegetarian_spotlight(self, limit: Optional[int] = None) -> List[Meal]:
        return list(
            self._base_queryset()
            .filter(is_vegetarian=True)
            .order_by("-restaurant__rating", "name")[: self._ensure_limit(limit)]
        )

    def mild_flavor(self, limit: Optional[int] = None) -> List[Meal]:
        return list(
            self._base_queryset()
            .filter(Q(is_spicy=False) | Q(is_spicy__isnull=True))
            .order_by("-restaurant__rating", "name")[: self._ensure_limit(limit)]
        )

    def new_experiences(self, limit: Optional[int] = None) -> List[Meal]:
        qs = self._base_queryset()
        if self.user:
            seen_ids = set(
                Favorite.objects.filter(user=self.user).values_list("meal_id", flat=True)
            )
            seen_ids.update(
                Review.objects.filter(user=self.user).values_list("meal_id", flat=True)
            )
            if seen_ids:
                qs = qs.exclude(pk__in=seen_ids)
        return list(qs.order_by("-created_at")[: self._ensure_limit(limit)])

    def describe_filters(self, filters: RecommendationFilters) -> str:
        parts: List[str] = []
        if filters.cuisine_type:
            parts.append(f"料理：{filters.cuisine_type}")
        if filters.price_range:
            display = dict(Restaurant.PriceRange.choices).get(filters.price_range, filters.price_range)
            parts.append(f"價格：{display}")
        if filters.city:
            parts.append(f"城市：{filters.city}")
        if filters.district:
            parts.append(f"區域：{filters.district}")
        if filters.is_vegetarian:
            parts.append("僅素食")
        if filters.avoid_spicy:
            parts.append("不辣")
        return " · ".join(parts) if parts else "隨機推薦"
