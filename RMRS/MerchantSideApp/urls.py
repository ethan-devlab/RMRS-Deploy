from django.urls import path

from .views import dashboard, login_view, register_view

app_name = "merchantsideapp"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard, name="dashboard"),
    path("", login_view, name="root"),
]
