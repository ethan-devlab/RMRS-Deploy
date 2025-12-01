from django.urls import path

from .views import (
    add_meal,
    delete_meal,
    dashboard,
    edit_meal,
    meal_detail,
    restaurant_detail,
    login_view,
    logout_view,
    manage_meals,
    register_view,
    settings,
    update_restaurant_status,
)

app_name = "merchantsideapp"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("meals/manage/", manage_meals, name="manage_meals"),
    path("meals/add/", add_meal, name="add_meal"),
    path("meals/<int:meal_id>/edit/", edit_meal, name="edit_meal"),
    path("meals/<int:meal_id>/delete/", delete_meal, name="delete_meal"),
    # Keep slug detail last so static routes like "manage" don't match it first.
    path("meals/<slug:meal_slug>/", meal_detail, name="meal_detail"),
    path("settings/", settings, name="settings"),
    path("restaurant/status/", update_restaurant_status, name="restaurant_status"),
    path("restaurants/<slug:restaurant_slug>/", restaurant_detail, name="restaurant_detail"),
    path("", login_view, name="root"),
]
