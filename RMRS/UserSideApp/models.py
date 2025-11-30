from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class AppUser(models.Model):
	"""Lightweight application user profile decoupled from Django auth."""

	username = models.CharField(max_length=50, unique=True)
	email = models.EmailField(max_length=100, unique=True)
	phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
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
	category = models.CharField(max_length=50, blank=True, null=True)
	price_range = models.CharField(
		max_length=1,
		choices=PriceRange.choices,
		blank=True,
		null=True,
	)
	is_vegetarian = models.BooleanField(default=False)
	avoid_spicy = models.BooleanField(default=False)
	recommendation_cooldown_days = models.PositiveSmallIntegerField(
		blank=True,
		null=True,
		help_text="Cooldown days before recommending the same meal again.",
		validators=[MinValueValidator(1), MaxValueValidator(30)],
	)
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


class DailyMealRecord(models.Model):
	"""Per-meal intake snapshot with macronutrient details."""

	class MealType(models.TextChoices):
		BREAKFAST = "breakfast", "早餐"
		LUNCH = "lunch", "午餐"
		DINNER = "dinner", "晚餐"
		SNACK = "snack", "點心"

	user = models.ForeignKey(
		AppUser,
		related_name="daily_meals",
		on_delete=models.CASCADE,
	)
	date = models.DateField(default=timezone.now)
	meal_type = models.CharField(max_length=16, choices=MealType.choices)
	meal_name = models.CharField(max_length=100)
	source_meal = models.ForeignKey(
		"MerchantSideApp.Meal",
		related_name="user_meal_records",
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
	)
	calories = models.DecimalField(max_digits=6, decimal_places=2, help_text="kcal")
	protein_grams = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		default=0,
		help_text="g",
	)
	carb_grams = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		default=0,
		help_text="g",
	)
	fat_grams = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		default=0,
		help_text="g",
	)
	meal_notes = models.TextField(blank=True, null=True)
	ingredients = models.JSONField(
		blank=True,
		null=True,
		help_text="List of ingredients or components with quantities.",
	)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	updated_at = models.DateTimeField(auto_now=True, db_default=Now())

	class Meta:
		db_table = "daily_meal_records"
		ordering = ["-date", "meal_type"]
		unique_together = ("user", "date", "meal_type", "meal_name")
		indexes = [
			models.Index(fields=["user", "date"], name="idx_meal_user_date"),
		]

	def __str__(self) -> str:
		return f"{self.user.username} {self.date} {self.meal_type}"


class MealComponent(models.Model):
	"""Breaks a meal record or merchant meal into named components for UI display."""

	meal_record = models.ForeignKey(
		DailyMealRecord,
		related_name="components",
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)
	meal = models.ForeignKey(
		"MerchantSideApp.Meal",
		related_name="nutrition_components",
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)
	name = models.CharField(max_length=100)
	quantity = models.CharField(max_length=50, blank=True, null=True)
	calories = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	metadata = models.JSONField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

	class Meta:
		db_table = "meal_components"
		indexes = [
			models.Index(fields=["meal_record"], name="idx_component_record"),
			models.Index(fields=["meal"], name="idx_component_meal"),
		]

	def clean(self):
		if not self.meal_record_id and not self.meal_id:
			raise ValidationError("必須指定飲食紀錄或餐點之一。")
		super().clean()

	def __str__(self) -> str:
		target = self.meal_record_id or self.meal_id
		return f"Component {self.name} -> {target}"


class WeeklyIntakeSummary(models.Model):
	"""Aggregated weekly intake to prevent duplicate totals."""

	user = models.ForeignKey(
		AppUser,
		related_name="weekly_intake",
		on_delete=models.CASCADE,
	)
	week_start = models.DateField(help_text="Week start date (Monday).")
	total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	total_protein = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	total_carbs = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	total_fat = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	meal_count = models.PositiveIntegerField(default=0)
	calculated_at = models.DateTimeField(auto_now_add=True, db_default=Now())

	class Meta:
		db_table = "weekly_intake_summaries"
		unique_together = ("user", "week_start")
		indexes = [models.Index(fields=["user", "week_start"], name="idx_weekly_user")]

	def __str__(self) -> str:
		return f"{self.user.username} {self.week_start}"


class NotificationSetting(models.Model):
	"""Per-user reminder configuration for push notifications."""

	class ReminderType(models.TextChoices):
		BREAKFAST = "breakfast", "早餐提醒"
		LUNCH = "lunch", "午餐提醒"
		DINNER = "dinner", "晚餐提醒"
		SNACK = "snack", "點心提醒"
		RANDOM = "random", "隨機推薦"

	class Channel(models.TextChoices):
		PUSH = "push", "推播"
		EMAIL = "email", "Email"
		SMS = "sms", "SMS"

	user = models.ForeignKey(
		AppUser,
		related_name="notification_settings",
		on_delete=models.CASCADE,
	)
	reminder_type = models.CharField(max_length=20, choices=ReminderType.choices)
	scheduled_time = models.TimeField(blank=True, null=True)
	is_enabled = models.BooleanField(default=True)
	channel = models.CharField(
		max_length=10,
		choices=Channel.choices,
		default=Channel.PUSH,
	)
	quiet_hours_start = models.TimeField(blank=True, null=True)
	quiet_hours_end = models.TimeField(blank=True, null=True)
	last_triggered_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	updated_at = models.DateTimeField(auto_now=True, db_default=Now())

	class Meta:
		db_table = "notification_settings"
		unique_together = ("user", "reminder_type")
		indexes = [models.Index(fields=["user"], name="idx_notify_settings_user")]

	def __str__(self) -> str:
		return f"Notification setting {self.reminder_type} for {self.user.username}"


class NotificationLog(models.Model):
	"""History of reminders/notifications delivered to the user."""

	class Status(models.TextChoices):
		SENT = "sent", "已發送"
		READ = "read", "已讀"
		FAILED = "failed", "失敗"

	user = models.ForeignKey(
		AppUser,
		related_name="notifications",
		on_delete=models.CASCADE,
	)
	setting = models.ForeignKey(
		NotificationSetting,
		related_name="logs",
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
	)
	title = models.CharField(max_length=120)
	body = models.TextField()
	notification_type = models.CharField(max_length=20, blank=True, null=True)
	status = models.CharField(
		max_length=10,
		choices=Status.choices,
		default=Status.SENT,
	)
	sent_at = models.DateTimeField(auto_now_add=True, db_default=Now())
	read_at = models.DateTimeField(blank=True, null=True)
	extra_payload = models.JSONField(blank=True, null=True)

	class Meta:
		db_table = "notification_logs"
		ordering = ["-sent_at"]
		indexes = [
			models.Index(fields=["user"], name="idx_notify_log_user"),
			models.Index(fields=["status"], name="idx_notify_log_status"),
		]

	def __str__(self) -> str:
		return f"Notification {self.title} -> {self.user.username}"

