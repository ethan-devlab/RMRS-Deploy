from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Now


class AppUser(models.Model):
	"""Lightweight application user profile decoupled from Django auth."""

	username = models.CharField(max_length=50, unique=True)
	email = models.EmailField(max_length=100, unique=True)
	password_hash = models.CharField(max_length=255)
	full_name = models.CharField(max_length=100, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	updated_at = models.DateTimeField(auto_now=True, db_default=Now())

	class Meta:
		db_table = "users"
		indexes = [
			models.Index(fields=["username"], name="idx_username"),
			models.Index(fields=["email"], name="idx_email"),
		]

	def __str__(self) -> str:
		return self.username


class UserPreference(models.Model):
	"""Stores per-user food preference filters."""

	class PriceRange(models.TextChoices):
		LOW = "低", "低"
		MEDIUM = "中", "中"
		HIGH = "高", "高"

	user = models.OneToOneField(
		AppUser,
		related_name="preferences",
		on_delete=models.CASCADE,
	)
	cuisine_type = models.CharField(max_length=50, blank=True, null=True)
	price_range = models.CharField(
		max_length=1,
		choices=PriceRange.choices,
		blank=True,
		null=True,
	)
	is_vegetarian = models.BooleanField(default=False)
	avoid_spicy = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	updated_at = models.DateTimeField(auto_now=True, db_default=Now())

	class Meta:
		db_table = "user_preferences"

	def __str__(self) -> str:
		return f"Preferences for {self.user.username}"


class Favorite(models.Model):
	"""Links a user to saved meals."""

	user = models.ForeignKey(
		AppUser,
		related_name="favorites",
		on_delete=models.CASCADE,
	)
	meal = models.ForeignKey(
		"MerchantSideApp.Meal",
		related_name="favorited_by",
		on_delete=models.CASCADE,
	)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

	class Meta:
		db_table = "favorites"
		unique_together = ("user", "meal")
		indexes = [models.Index(fields=["user"], name="idx_favorites_user")]

	def __str__(self) -> str:
		return f"{self.user.username} -> {self.meal_id}"


class Review(models.Model):
	"""Captures user generated meal feedback."""

	user = models.ForeignKey(
		AppUser,
		related_name="reviews",
		on_delete=models.CASCADE,
	)
	meal = models.ForeignKey(
		"MerchantSideApp.Meal",
		related_name="reviews",
		on_delete=models.CASCADE,
	)
	restaurant = models.ForeignKey(
		"MerchantSideApp.Restaurant",
		related_name="reviews",
		on_delete=models.CASCADE,
	)
	rating = models.PositiveSmallIntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(5)]
	)
	comment = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	updated_at = models.DateTimeField(auto_now=True, db_default=Now())

	class Meta:
		db_table = "reviews"
		unique_together = ("user", "meal")
		indexes = [
			models.Index(fields=["meal"], name="idx_reviews_meal"),
			models.Index(fields=["restaurant"], name="idx_reviews_restaurant"),
		]

	def __str__(self) -> str:
		return f"Review {self.rating} by {self.user.username}"

