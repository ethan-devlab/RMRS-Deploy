from .auth import login_view, register_view
from .dashboard import (
	health_advice,
	home,
	notifications,
	random_recommendation,
	record_meal,
	search_restaurants,
	settings,
	today_meal,
)

__all__ = [
	"login_view",
	"register_view",
	"home",
	"search_restaurants",
	"random_recommendation",
	"today_meal",
	"record_meal",
	"notifications",
	"health_advice",
	"settings",
]
