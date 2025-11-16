from django.urls import path

from .views import (
    health_advice,
    home,
    login_view,
    notifications,
    random_recommendation,
    record_meal,
    register_view,
    search_restaurants,
    settings,
    today_meal,
)

app_name = "usersideapp"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("search/", search_restaurants, name="search"),
    path("random/", random_recommendation, name="random"),
    path("today/", today_meal, name="today"),
    path("record/", record_meal, name="record"),
    path("notify/", notifications, name="notify"),
    path("health/", health_advice, name="health"),
    path("settings/", settings, name="settings"),
    path("", home, name="home"),
]
