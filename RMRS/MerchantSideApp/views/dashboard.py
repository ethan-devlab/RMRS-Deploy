from django.shortcuts import render


def dashboard(request):
    return render(request, "merchantsideapp/dashboard.html")


def add_meal(request):
    return render(request, "merchantsideapp/add_meal.html")


def manage_meals(request):
    return render(request, "merchantsideapp/manage_meals.html")
