"""Shared utility functions for MerchantSideApp views."""

import json
from decimal import Decimal

from ..models import NutritionInfo
from UserSideApp.models import MealComponent


def _build_display_nutrition(meal):
    """Build nutrition display data for a meal."""
    nutrition_info = getattr(meal, "nutrition", None)
    if not nutrition_info:
        return None
    return {
        "calories": nutrition_info.calories,
        "protein": nutrition_info.protein,
        "fat": nutrition_info.fat,
        "carbs": getattr(nutrition_info, "carbohydrate", None),
        "sodium": nutrition_info.sodium,
        "fiber": getattr(nutrition_info, "fiber", None),
    }


def _extract_ingredients(meal_components):
    """Extract ingredients and allergens from meal components."""
    ingredients = []
    allergens = []
    for component in meal_components:
        label = component.name
        if component.quantity:
            label = f"{label}（{component.quantity}）"
        ingredients.append(label)
        metadata = component.metadata or {}
        allergen_payload = metadata.get("allergens")
        if isinstance(allergen_payload, (list, tuple)):
            allergens.extend(str(item) for item in allergen_payload if item)
        elif allergen_payload:
            allergens.append(str(allergen_payload))
    deduped = []
    seen = set()
    for item in allergens:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return ingredients, deduped


def _coerce_decimal(value: Decimal | float | str | int | None) -> Decimal:
    """Coerce a value to Decimal."""
    if isinstance(value, Decimal):
        return value
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def _coerce_float(value: Decimal | float | str | int | None) -> float | None:
    """Coerce a value to float."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None


def _persist_meal_nutrition(meal, entries):
    """Persist meal nutrition information."""
    if not entries:
        NutritionInfo.objects.filter(meal=meal).delete()
        return

    has_nutrition = False
    totals = {
        "calories": Decimal("0"),
        "protein": Decimal("0"),
        "carbohydrate": Decimal("0"),
        "fat": Decimal("0"),
    }

    for entry in entries:
        calories = entry.get("calories")
        if calories is not None:
            totals["calories"] += _coerce_decimal(calories)
            has_nutrition = has_nutrition or _coerce_decimal(calories) > 0
        for source_key, total_key in (("protein", "protein"), ("carb", "carbohydrate"), ("fat", "fat")):
            macro_value = entry.get(source_key)
            if macro_value is not None:
                totals[total_key] += _coerce_decimal(macro_value)
                has_nutrition = True

    if not has_nutrition:
        NutritionInfo.objects.filter(meal=meal).delete()
        return

    existing = getattr(meal, "nutrition", None)
    if existing is None:
        existing = NutritionInfo.objects.filter(meal=meal).first()
    sodium_value = getattr(existing, "sodium", Decimal("0")) if existing else Decimal("0")

    breakdown_payload = [
        {
            "name": entry.get("name"),
            "quantity": entry.get("quantity"),
            "calories": _coerce_float(entry.get("calories")) or 0.0,
            "protein": _coerce_float(entry.get("protein")),
            "carb": _coerce_float(entry.get("carb")),
            "fat": _coerce_float(entry.get("fat")),
            "notes": entry.get("notes"),
        }
        for entry in entries
    ]

    NutritionInfo.objects.update_or_create(
        meal=meal,
        defaults={
            "calories": totals["calories"],
            "protein": totals["protein"],
            "fat": totals["fat"],
            "carbohydrate": totals["carbohydrate"],
            "sodium": sodium_value,
            "breakdown": breakdown_payload,
        },
    )


def _persist_nutrition_components(meal, entries):
    """Persist nutrition components for a meal."""
    MealComponent.objects.filter(meal=meal).delete()
    if entries:
        MealComponent.objects.bulk_create(
            [
                MealComponent(
                    meal=meal,
                    name=entry["name"],
                    quantity=entry["quantity"],
                    calories=entry["calories"],
                    metadata=entry["metadata"],
                )
                for entry in entries
            ],
        )
    _persist_meal_nutrition(meal, entries)


def _build_nutrition_payload(meal):
    """Build JSON payload for nutrition editor."""
    nutrition = getattr(meal, "nutrition", None)
    if nutrition and nutrition.breakdown:
        return json.dumps(nutrition.breakdown, ensure_ascii=False)

    entries = []
    for component in meal.nutrition_components.all().order_by("id"):
        metadata = component.metadata or {}
        entries.append(
            {
                "name": component.name,
                "quantity": component.quantity,
                "calories": float(component.calories),
                "protein": metadata.get("protein"),
                "carb": metadata.get("carb"),
                "fat": metadata.get("fat"),
                "notes": metadata.get("notes"),
            }
        )
    return json.dumps(entries, ensure_ascii=False)
