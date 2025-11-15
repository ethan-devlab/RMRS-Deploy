from django.db import models
from django.db.models.functions import Now


class RecommendationHistory(models.Model):
	"""Keeps a trace of meal suggestions shown to users."""

	user = models.ForeignKey(
		"UserSideApp.AppUser",
		related_name="recommendations",
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
	)
	meal = models.ForeignKey(
		"MerchantSideApp.Meal",
		related_name="recommendation_events",
		on_delete=models.CASCADE,
	)
	restaurant = models.ForeignKey(
		"MerchantSideApp.Restaurant",
		related_name="recommendation_events",
		on_delete=models.CASCADE,
	)
	recommended_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	was_selected = models.BooleanField(default=False, db_default=False)

	class Meta:
		db_table = "recommendation_history"
		indexes = [
			models.Index(fields=["user"], name="idx_rec_history_user"),
			models.Index(fields=["recommended_at"], name="idx_recommended_at"),
		]

	def __str__(self) -> str:
		base = f"Meal {self.meal_id} for restaurant {self.restaurant_id}"
		return f"{base} at {self.recommended_at:%Y-%m-%d %H:%M:%S}"
