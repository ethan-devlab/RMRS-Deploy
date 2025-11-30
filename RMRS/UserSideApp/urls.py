from django.urls import path

from .views import (
    health_advice,
    home,
    interactions,
    login_view,
    logout_view,
    notifications,
    random_recommendation,
    random_recommendation_data,
    record_meal,
    register_view,
    restaurant_meals_api,
    search_restaurants,
    settings,
    today_meal,
)

app_name = "usersideapp"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("search/", search_restaurants, name="search"),
    path("random/", random_recommendation, name="random"),
    path("random/data/", random_recommendation_data, name="random_data"),
    path("today/", today_meal, name="today"),
    path("record/", record_meal, name="record"),
    path("record/restaurant-meals/", restaurant_meals_api, name="restaurant_meals_api"),
    path("notify/", notifications, name="notify"),
    path("health/", health_advice, name="health"),
    path("interactions/", interactions, name="interactions"),
    path("settings/", settings, name="settings"),
    path("", home, name="home"),
]
