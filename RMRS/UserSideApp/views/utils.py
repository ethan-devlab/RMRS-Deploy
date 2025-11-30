"""Shared utility functions and constants for UserSideApp views."""

import json

from django.shortcuts import render

from ..auth_utils import get_current_user
from ..models import DailyMealRecord, MealComponent


# Constants
DEFAULT_MAP_CENTER = (23.6978, 120.9605)
MAX_MAP_RESULTS = 50
MAX_MEAL_RESULTS = 40


def _serialize_components(record: DailyMealRecord) -> str:
    """Serialize meal components to JSON string."""
    component_qs = record.components.all()
    return json.dumps(
        [
            {
                "name": component.name,
                "quantity": component.quantity or "",
                "calories": str(component.calories),
            }
            for component in component_qs
        ],
        ensure_ascii=False,
    )


def _save_components(record: DailyMealRecord, components_data):
    """Save meal components for a record."""
    MealComponent.objects.filter(meal_record=record).delete()
    if not components_data:
        return
    MealComponent.objects.bulk_create(
        [
            MealComponent(
                meal_record=record,
                name=component["name"],
                quantity=component.get("quantity"),
                calories=component.get("calories", 0),
            )
            for component in components_data
        ]
    )


def _render(request, template_name: str, active_nav: str, extra: dict | None = None):
    """Render template with common context."""
    context = {
        "active_nav": active_nav,
        "current_user": get_current_user(request),
    }
    if extra:
        context.update(extra)
    return render(request, template_name, context)


def _collect_form_errors(form) -> dict:
    """Collect form errors as a dictionary."""
    if not form.is_bound or form.is_valid():
        return {}
    errors = {}
    for field, field_errors in form.errors.items():
        errors[field] = [str(error) for error in field_errors]
    return errors
