from django.shortcuts import render


def login_view(request):
    return render(request, "merchantsideapp/login.html")


def register_view(request):
    return render(request, "merchantsideapp/register.html")
