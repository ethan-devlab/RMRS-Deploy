from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Now


class Restaurant(models.Model):
    """Merchant managed restaurant metadata."""

    class PriceRange(models.TextChoices):
        LOW = "低", "低"
        MEDIUM = "中", "中"
        HIGH = "高", "高"

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cuisine_type = models.CharField(max_length=50, blank=True, null=True)
    price_range = models.CharField(
        max_length=1,
        choices=PriceRange.choices,
        default=PriceRange.MEDIUM,
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "restaurants"
        indexes = [
            models.Index(fields=["cuisine_type"], name="idx_cuisine_type"),
            models.Index(fields=["price_range"], name="idx_price_range"),
            models.Index(fields=["is_active"], name="idx_is_active"),
            models.Index(fields=["city", "district"], name="idx_city_district"),
            models.Index(fields=["latitude", "longitude"], name="idx_geo_coordinates"),
        ]

    def __str__(self) -> str:
        return self.name


class Meal(models.Model):
    """Individual dishes offered by a restaurant."""

    restaurant = models.ForeignKey(
        Restaurant,
        related_name="meals",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    is_available = models.BooleanField(default=True, db_default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())
    tags = models.ManyToManyField(
        "Tag",
        related_name="meals",
        through="MealTag",
        blank=True,
    )

    class Meta:
        db_table = "meals"
        indexes = [
            models.Index(fields=["restaurant"], name="idx_meals_restaurant"),
            models.Index(fields=["category"], name="idx_category"),
            models.Index(fields=["is_vegetarian"], name="idx_is_vegetarian"),
            models.Index(fields=["is_available"], name="idx_is_available"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.restaurant.name})"


class NutritionInfo(models.Model):
    """Per-meal nutrition metrics to power health-focused flows."""

    meal = models.OneToOneField(
        Meal,
        related_name="nutrition",
        on_delete=models.CASCADE,
    )
    calories = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    protein = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    fat = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    carbohydrate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    sodium = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "nutrition_info"
        indexes = [
            models.Index(fields=["calories"], name="idx_nutrition_calories"),
        ]

    def __str__(self) -> str:
        return f"NutritionInfo<{self.meal_id}>"


class Tag(models.Model):
    """Tag taxonomy used to enrich meals."""

    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())

    class Meta:
        db_table = "tags"

    def __str__(self) -> str:
        return self.name


class MealTag(models.Model):
    """Explicit through table tying meals to tags."""

    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "meal_tags"
        unique_together = ("meal", "tag")

    def __str__(self) -> str:
        return f"{self.meal_id}:{self.tag_id}"


class MerchantAccount(models.Model):
    """Authentication profile for merchants tied to a single restaurant."""

    restaurant = models.OneToOneField(
        Restaurant,
        related_name="merchant_account",
        on_delete=models.CASCADE,
    )
    merchant_name = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Human-friendly merchant handle used during login.",
    )
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True, db_default=Now())

    class Meta:
        db_table = "merchant_accounts"
        indexes = [
            models.Index(fields=["email"], name="idx_merchant_email"),
        ]

    def __str__(self) -> str:
        return f"{self.merchant_name or self.email} -> {self.restaurant_id}"
