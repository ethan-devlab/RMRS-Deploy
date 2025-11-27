from django.urls import path

from .views import (
    add_meal,
    dashboard,
    login_view,
    logout_view,
    manage_meals,
    register_view,
)

app_name = "merchantsideapp"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("meals/add/", add_meal, name="add_meal"),
    path("meals/manage/", manage_meals, name="manage_meals"),
    path("", login_view, name="root"),
]
