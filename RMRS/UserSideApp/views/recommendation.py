"""Recommendation views for UserSideApp."""

from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from RecommendationSystem.services import get_recommendation_cooldown_days

from ..auth_utils import get_current_user, user_login_required
from ..forms import RecommendationFilterForm
from ..services import RecommendationEngine
from .utils import _render, _collect_form_errors


def _build_recommendation_cards(meals, reason: str, used_ids: set[int] | None = None):
    """Build recommendation card data from meals."""
    used_ids = used_ids or set()
    cards = []
    for meal in meals:
        if meal.id in used_ids:
            continue
        cards.append(
            {
                "meal": meal,
                "restaurant": meal.restaurant,
                "favorite_count": getattr(meal, "favorite_count", 0) or 0,
                "reason": reason,
            }
        )
        used_ids.add(meal.id)
    return cards


def _serialize_card(card: dict) -> dict:
    """Serialize a recommendation card to JSON-compatible dict."""
    meal = card["meal"]
    restaurant = card["restaurant"]
    price_label = ""
    if getattr(restaurant, "price_range", None):
        try:
            price_label = restaurant.get_price_range_display()
        except Exception:  # pragma: no cover - defensive
            price_label = restaurant.price_range
    meal_url = reverse("merchantsideapp:meal_detail", args=[meal.slug])
    restaurant_url = reverse("merchantsideapp:restaurant_detail", args=[restaurant.slug])
    return {
        "meal": {
            "id": meal.id,
            "slug": meal.slug,
            "name": meal.name,
            "description": meal.description or "",
            "isVegetarian": bool(meal.is_vegetarian),
            "isSpicy": bool(meal.is_spicy),
            "url": meal_url,
        },
        "restaurant": {
            "id": restaurant.id,
            "slug": restaurant.slug,
            "name": restaurant.name,
            "cuisineType": restaurant.cuisine_type or "",
            "priceRange": restaurant.price_range or "",
            "priceLabel": price_label or "",
            "city": restaurant.city or "",
            "district": restaurant.district or "",
            "url": restaurant_url,
        },
        "favoriteCount": card.get("favorite_count", 0),
        "reason": card.get("reason") or "",
    }


def _build_random_context(user, data=None):
    """Build context for random recommendation page."""
    engine = RecommendationEngine(user)
    preference = getattr(user, "preferences", None)
    initial_data = engine.initial_data(preference)
    filter_form = RecommendationFilterForm(initial=initial_data)
    filters_used = engine.filters_from_data(initial_data)
    primary_reason = "根據你的偏好"
    primary_meals = []
    recommendation_alert = None
    action = (data or {}).get("action") if data else None
    cooldown_days = get_recommendation_cooldown_days(user)

    if data:
        if action == "use_preferences":
            filters_used = engine.filters_from_preferences(preference, (data or {}).get("limit"))
            primary_meals = engine.preference_recommendations(filters_used.limit)
            primary_reason = "根據你的偏好"
        elif action == "surprise":
            primary_meals = engine.random_meals((data or {}).get("limit") or filters_used.limit)
            primary_reason = "驚喜推薦"
        else:
            filter_form = RecommendationFilterForm(data=data, initial=initial_data)
            if filter_form.is_valid():
                filters_used = engine.filters_from_data(filter_form.cleaned_data)
                primary_meals = engine.apply_filters(filters_used)
                primary_reason = engine.describe_filters(filters_used)
            else:
                primary_meals = []
    else:
        primary_meals = engine.preference_recommendations(filters_used.limit)

    if not primary_meals:
        primary_meals = engine.popular_meals(filters_used.limit)
        recommendation_alert = "目前找不到符合條件的餐點，先為你帶來熱門選擇。"
        primary_reason = "熱門推薦"

    used_ids: set[int] = set()
    primary_cards = _build_recommendation_cards(primary_meals, primary_reason, used_ids)

    sections_config = [
        ("熱門收藏", "依收藏數排序", engine.popular_meals(4)),
        ("親民價位", "低價位也能享受美味", engine.budget_friendly(4)),
        ("素食推薦", "友善素食選擇", engine.vegetarian_spotlight(4)),
        ("清爽不辣", "適合想吃清淡的一天", engine.mild_flavor(4)),
        ("新的體驗", "你尚未收藏或評論過", engine.new_experiences(4)),
    ]
    secondary_sections = []
    for title, subtitle, meals in sections_config:
        cards = _build_recommendation_cards(meals, subtitle, used_ids)
        if cards:
            secondary_sections.append(
                {
                    "title": title,
                    "subtitle": subtitle,
                    "cards": cards,
                }
            )

    preference_snapshot = None
    if preference:
        parts = []
        if preference.cuisine_type:
            parts.append(preference.cuisine_type)
        if preference.category:
            parts.append(f"品項 {preference.category}")
        if preference.price_range:
            parts.append(f"價格 {preference.price_range}")
        if preference.is_vegetarian:
            parts.append("素食")
        if preference.avoid_spicy:
            parts.append("不辣")
        preference_snapshot = " · ".join(parts) if parts else "尚未設定明確條件"

    return {
        "filter_form": filter_form,
        "primary_recommendations": primary_cards,
        "primary_reason": primary_reason,
        "secondary_sections": secondary_sections,
        "recommendation_alert": recommendation_alert,
        "preference_snapshot": preference_snapshot,
        "cooldown_days": cooldown_days,
    }


@user_login_required
def random_recommendation(request):
    """Display random meal recommendations."""
    user = get_current_user(request)
    form_data = request.POST if request.method == "POST" else None
    context = _build_random_context(user, form_data)
    return _render(
        request,
        "usersideapp/random.html",
        "random",
        context,
    )


@require_POST
@user_login_required
def random_recommendation_data(request):
    """API endpoint for recommendation data."""
    user = get_current_user(request)
    context = _build_random_context(user, request.POST)
    data = {
        "primary": {
            "reason": context["primary_reason"],
            "cards": [_serialize_card(card) for card in context["primary_recommendations"]],
        },
        "secondary": [
            {
                "title": section["title"],
                "subtitle": section["subtitle"],
                "cards": [_serialize_card(card) for card in section["cards"]],
            }
            for section in context["secondary_sections"]
        ],
        "alert": context["recommendation_alert"],
        "preferenceSnapshot": context["preference_snapshot"],
        "formErrors": _collect_form_errors(context["filter_form"]),
        "cooldownDays": context["cooldown_days"],
    }
    return JsonResponse(data)
