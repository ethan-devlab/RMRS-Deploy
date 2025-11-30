from .auth import login_view, logout_view, register_view
from .dashboard import dashboard
from .meals import add_meal, delete_meal, edit_meal, manage_meals, meal_detail
from .merchant_settings import settings
from .restaurant import restaurant_detail, update_restaurant_status

__all__ = [
    "login_view",
    "register_view",
    "logout_view",
    "dashboard",
    "add_meal",
    "edit_meal",
    "delete_meal",
    "manage_meals",
    "meal_detail",
    "restaurant_detail",
    "update_restaurant_status",
    "settings",
]
