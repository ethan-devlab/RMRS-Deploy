from .auth import login_view, logout_view, register_view
from .dashboard import (
	add_meal,
	dashboard,
	delete_meal,
	edit_meal,
	manage_meals,
	settings,
	update_restaurant_status,
)

__all__ = [
	"login_view",
	"register_view",
	"logout_view",
	"dashboard",
	"add_meal",
	"edit_meal",
	"delete_meal",
	"manage_meals",
	"settings",
	"update_restaurant_status",
]
