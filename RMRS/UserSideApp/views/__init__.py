from .auth import login_view, logout_view, register_view
from .dashboard import (
	health_advice,
	home,
	interactions,
	notifications,
	random_recommendation,
	random_recommendation_data,
	record_meal,
	search_restaurants,
	settings,
	today_meal,
)

__all__ = [
	"login_view",
	"logout_view",
	"register_view",
	"home",
	"search_restaurants",
	"random_recommendation",
	"random_recommendation_data",
	"today_meal",
	"record_meal",
	"notifications",
	"health_advice",
	"interactions",
	"settings",
]
