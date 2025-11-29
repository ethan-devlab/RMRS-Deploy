from django.urls import path

from .views import (
    add_meal,
    delete_meal,
    dashboard,
    edit_meal,
    login_view,
    logout_view,
    manage_meals,
    register_view,
    update_restaurant_status,
)

app_name = "merchantsideapp"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("meals/add/", add_meal, name="add_meal"),
    path("meals/<int:meal_id>/edit/", edit_meal, name="edit_meal"),
    path("meals/<int:meal_id>/delete/", delete_meal, name="delete_meal"),
    path("meals/manage/", manage_meals, name="manage_meals"),
    path("restaurant/status/", update_restaurant_status, name="restaurant_status"),
    path("", login_view, name="root"),
]
