from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta
from typing import Dict, List, Optional, Tuple

from django.db.models import Count, Q, Sum
from django.utils import timezone

from MerchantSideApp.models import Meal, Restaurant
from RecommendationSystem.services import recent_selected_meal_ids

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


def build_health_summary(user: AppUser, days: int = 7) -> Dict[str, object]:
    today = timezone.now().date()
    window_days = max(1, days)
    start_date = today - timedelta(days=window_days - 1)
    records = DailyMealRecord.objects.filter(user=user, date__gte=start_date)
    has_data = records.exists()
    range_label = f"最近 {window_days} 天"
    if not has_data:
        return {
            "has_data": False,
            "range_label": range_label,
            "status_label": "尚未有資料",
            "status_tone": "neutral",
            "tags": [],
            "today_tip": {
                "icon": "🌱",
                "title": "開始記錄，取得專屬建議",
                "description": "目前尚未有飲食紀錄，先從記錄今日的餐點開始，系統就能幫你整理分析。",
                "actions": [
                    "每天至少填寫 2〜3 餐，幾天後就能看到趨勢",
                    "提供熱量與營養素數值可獲得更精準的提醒",
                ],
            },
            "nutrition_sections": [
                {
                    "icon": "🥦",
                    "title": "蔬菜攝取",
                    "body": "記錄每餐時也可以順手寫下蔬菜份量，系統會提醒是否達到半盤蔬菜的習慣。",
                    "suggestions": [
                        "便當/外食時主動加點一份燙青菜",
                        "火鍋或滷味記得選擇深綠色蔬菜",
                    ],
                },
                {
                    "icon": "🍚",
                    "title": "碳水與澱粉",
                    "body": "輸入飯、麵或飲料的份量，可以幫助系統偵測碳水佔比是否過高。",
                    "suggestions": [
                        "從八分滿白飯或半份麵開始調整",
                        "含糖飲料可改成無糖茶或氣泡水",
                    ],
                },
                {
                    "icon": "🍗",
                    "title": "蛋白質補充",
                    "body": "每餐加上一份掌心大小的蛋白質來源，有助於維持肌肉量。",
                    "suggestions": [
                        "午晚餐各加一份雞胸肉、魚或豆腐",
                        "下午點心可改成無糖豆漿、優格",
                    ],
                },
            ],
            "lifestyle_tips": [
                "設定喝水目標 1500〜2000 ml，分多次補充",
                "久坐族每 60 分鐘起身活動 3 分鐘",
            ],
        }

    totals = records.aggregate(
        total_calories=Sum("calories"),
        total_protein=Sum("protein_grams"),
        total_carbs=Sum("carb_grams"),
        total_fat=Sum("fat_grams"),
    )
    total_calories = float(totals["total_calories"] or 0)
    total_protein = float(totals["total_protein"] or 0)
    total_carbs = float(totals["total_carbs"] or 0)
    total_fat = float(totals["total_fat"] or 0)
    active_days = max(1, records.values("date").distinct().count())
    avg_calories = total_calories / active_days if active_days else 0
    avg_protein = total_protein / active_days if active_days else 0
    avg_carbs = total_carbs / active_days if active_days else 0
    avg_fat = total_fat / active_days if active_days else 0
    avg_meals = records.count() / active_days if active_days else 0

    macro_calories = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
    macro_calories = macro_calories or 1
    protein_ratio = (total_protein * 4) / macro_calories
    carb_ratio = (total_carbs * 4) / macro_calories
    fat_ratio = (total_fat * 9) / macro_calories

    if avg_calories < 1300:
        status_label = "熱量略偏低"
        status_tone = "caution"
    elif avg_calories > 2300:
        status_label = "熱量略偏高"
        status_tone = "caution"
    else:
        status_label = "普通偏健康"
        status_tone = "good"

    tags: List[Dict[str, str]] = []
    if protein_ratio < 0.18:
        tags.append({"text": "蛋白質略不足", "tone": "blue"})
    elif protein_ratio > 0.28:
        tags.append({"text": "蛋白質充足", "tone": "green"})
    else:
        tags.append({"text": "蛋白質穩定", "tone": "green"})

    if carb_ratio > 0.55:
        tags.append({"text": "碳水偏多", "tone": "yellow"})
    elif carb_ratio < 0.45:
        tags.append({"text": "碳水略低", "tone": "blue"})
    else:
        tags.append({"text": "碳水平衡", "tone": "green"})

    if avg_meals >= 3:
        tags.append({"text": "飲食紀錄規律", "tone": "green"})
    else:
        tags.append({"text": "紀錄可再充實", "tone": "yellow"})

    def select_focus_tip() -> Dict[str, object]:
        deviations = []
        if protein_ratio < 0.18:
            deviations.append(("protein_low", 0.18 - protein_ratio))
        if carb_ratio > 0.55:
            deviations.append(("carb_high", carb_ratio - 0.55))
        if avg_calories < 1300:
            deviations.append(("cal_low", (1300 - avg_calories) / 1300))
        if avg_meals < 3:
            deviations.append(("logging_low", 3 - avg_meals))
        if not deviations:
            return {
                "icon": "🌤️",
                "title": "維持均衡的黃金三角",
                "description": (
                    "本週整體數據穩定，持續維持『有菜、有蛋白質、有主食』的配餐即可。"
                ),
                "actions": [
                    "午、晚餐各保留一份掌心大小蛋白質",
                    "每餐至少半碗蔬菜，顏色越多越好",
                    "外食時留意含糖飲料的頻率",
                ],
            }
        focus_key = max(deviations, key=lambda item: item[1])[0]
        if focus_key == "protein_low":
            return {
                "icon": "🍗",
                "title": "今天多補一份蛋白質",
                "description": (
                    "最近每餐蛋白質偏少，可以從早餐或下午點心加蛋、豆漿或優格開始。"
                ),
                "actions": [
                    "午晚餐優先選擇有雞肉、魚或豆腐的主菜",
                    "下午加餐可改成無糖豆漿或希臘優格",
                    "每餐至少有一份掌心大小的蛋白質",
                ],
            }
        if focus_key == "carb_high":
            return {
                "icon": "🍚",
                "title": "澱粉份量微調",
                "description": "碳水佔比略高，試著將白飯減少 2〜3 口或改成半碗糙米。",
                "actions": [
                    "點便當時請店家少飯或加青菜",
                    "含糖飲料改成無糖／微糖，減少額外熱量",
                    "晚餐記得在 20:00 前結束，避免宵夜",
                ],
            }
        if focus_key == "cal_low":
            return {
                "icon": "🥗",
                "title": "熱量略低，加點能量",
                "description": "平均熱量偏低，記得補充全穀根莖或健康脂肪來源。",
                "actions": [
                    "早餐加入全麥吐司或地瓜",
                    "沙拉可以加酪梨、堅果或初榨橄欖油",
                    "運動日記得多補一餐高蛋白點心",
                ],
            }
        return {
            "icon": "📝",
            "title": "多記錄幾餐，建議更準確",
            "description": "平均每天僅記錄 {:.1f} 餐，建議補齊三餐讓建議更完整。".format(avg_meals),
            "actions": [
                "設定提醒，餐後 5 分鐘內完成紀錄",
                "若忘記實際份量，可先估算後再修正",
                "照片或文字都能幫助回顧飲食",
            ],
        }

    today_tip = select_focus_tip()

    nutrition_sections = [
        {
            "icon": "🥦",
            "title": "蔬菜與纖維",
            "body": (
                f"過去 {active_days} 天平均每餐記錄 {avg_meals:.1f} 次，建議繼續維持『半盤蔬菜』的習慣。"
            ),
            "suggestions": [
                "外食選項可優先有兩種以上青菜的店家",
                "火鍋/滷味時加點深色蔬菜，增加纖維",
            ],
        },
        {
            "icon": "🍚",
            "title": "碳水與澱粉",
            "body": (
                f"碳水約佔總熱量的 {carb_ratio * 100:.0f}%，{ '略高' if carb_ratio > 0.55 else '維持在合理範圍'}。"
            ),
            "suggestions": [
                "午晚餐可從八分滿飯量或半份麵開始調整",
                "下午若想吃甜點，可搭配無糖飲品降低總糖量",
            ],
        },
        {
            "icon": "🍗",
            "title": "蛋白質補充",
            "body": (
                f"平均每天蛋白質約 {avg_protein:.0f} g，可作為維持肌力的基礎，再視需求加強。"
            ),
            "suggestions": [
                "早餐加入蛋、豆漿或優格，均衡三餐",
                "午晚餐固定保留掌心大小的蛋白質來源",
            ],
        },
    ]

    lifestyle_tips = [
        "久坐族每 60 分鐘起身活動 3〜5 分鐘",
        "設定喝水目標 1500〜2000 ml，分批補充",
    ]
    if avg_meals < 3:
        lifestyle_tips.insert(0, "每天至少記錄三餐，系統才能給出更完整分析。")
    if avg_calories > 2300:
        lifestyle_tips.append("晚餐後減少加餐，避免多餘熱量囤積。")

    return {
        "has_data": True,
        "range_label": range_label,
        "status_label": status_label,
        "status_tone": status_tone,
        "tags": tags,
        "today_tip": today_tip,
        "nutrition_sections": nutrition_sections,
        "lifestyle_tips": lifestyle_tips,
        "averages": {
            "calories": round(avg_calories),
            "protein": round(avg_protein),
            "carbs": round(avg_carbs),
            "fat": round(avg_fat),
            "meals_per_day": round(avg_meals, 1),
        },
    }


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
    category: Optional[str] = None
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
        qs = (
            Meal.objects.filter(is_available=True, restaurant__is_active=True)
            .select_related("restaurant")
            .annotate(favorite_count=Count("favorited_by"))
        )
        if getattr(self.user, "pk", None):
            recent_ids = recent_selected_meal_ids(self.user)
            qs = qs.exclude(pk__in=recent_ids)
        return qs

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
            "category": (pref.category if pref and pref.category else ""),
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
            category=str(data.get("category") or "").strip() or None,
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
            category=preference.category or None,
            price_range=preference.price_range or None,
            is_vegetarian=preference.is_vegetarian,
            avoid_spicy=preference.avoid_spicy,
            limit=self._ensure_limit(limit),
        )

    def apply_filters(self, filters: RecommendationFilters) -> List[Meal]:
        qs = self._base_queryset()
        if filters.cuisine_type:
            qs = qs.filter(restaurant__cuisine_type__icontains=filters.cuisine_type)
        if filters.category:
            qs = qs.filter(category__iexact=filters.category)
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
            .order_by("?")
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
        if filters.category:
            parts.append(f"品項：{filters.category}")
        if filters.city:
            parts.append(f"城市：{filters.city}")
        if filters.district:
            parts.append(f"區域：{filters.district}")
        if filters.is_vegetarian:
            parts.append("僅素食")
        if filters.avoid_spicy:
            parts.append("不辣")
        return " · ".join(parts) if parts else "隨機推薦"
