from .auth import login_view, logout_view, register_view
from .health import health_advice
from .home import home
from .interactions import interactions
from .meals import record_meal, restaurant_meals_api, today_meal
from .notifications import notifications
from .recommendation import random_recommendation, random_recommendation_data
from .search import search_restaurants
from .user_settings import settings

__all__ = [
    "login_view",
    "logout_view",
    "register_view",
    "home",
    "search_restaurants",
    "random_recommendation",
    "random_recommendation_data",
    "today_meal",
    "record_meal",
    "restaurant_meals_api",
    "notifications",
    "health_advice",
    "interactions",
    "settings",
]
