from django.shortcuts import render


def _render(request, template_name: str, active_nav: str):
    return render(request, template_name, {"active_nav": active_nav})


def home(request):
    return _render(request, "usersideapp/home.html", "home")


def search_restaurants(request):
    return _render(request, "usersideapp/search.html", "search")


def random_recommendation(request):
    return _render(request, "usersideapp/random.html", "random")


def today_meal(request):
    return _render(request, "usersideapp/today_meal.html", "today")


def record_meal(request):
    return _render(request, "usersideapp/record_meal.html", "record")


def notifications(request):
    return _render(request, "usersideapp/notify.html", "notify")


def health_advice(request):
    return _render(request, "usersideapp/health.html", "health")


def settings(request):
    return _render(request, "usersideapp/settings.html", "settings")
