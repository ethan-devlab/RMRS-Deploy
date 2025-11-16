from django.shortcuts import render


def login_view(request):
    return render(request, "usersideapp/login.html")


def register_view(request):
    return render(request, "usersideapp/register.html")
