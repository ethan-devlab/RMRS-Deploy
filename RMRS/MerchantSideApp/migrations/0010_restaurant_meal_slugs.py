from django.db import migrations, models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

SLUG_MAX_LENGTH = 150
SLUG_BASE_LENGTH = SLUG_MAX_LENGTH - 6


def _build_unique_slug(model_cls, base_value, fallback_prefix, exclude_pk=None):
    base_slug = slugify(base_value or "")[:SLUG_BASE_LENGTH]
    if not base_slug:
        base_slug = f"{fallback_prefix}-{get_random_string(6)}"
    slug_candidate = base_slug
    while model_cls.objects.filter(slug=slug_candidate).exclude(pk=exclude_pk).exists():
        slug_candidate = f"{base_slug}-{get_random_string(4)}"
        slug_candidate = slug_candidate[:SLUG_MAX_LENGTH]
    return slug_candidate


def populate_slugs(apps, schema_editor):
    Restaurant = apps.get_model("MerchantSideApp", "Restaurant")
    Meal = apps.get_model("MerchantSideApp", "Meal")

    for restaurant in Restaurant.objects.all().iterator():
        restaurant.slug = _build_unique_slug(Restaurant, restaurant.name, "restaurant", exclude_pk=restaurant.pk)
        restaurant.save(update_fields=["slug"])

    for meal in Meal.objects.select_related("restaurant").all().iterator():
        restaurant_name = getattr(meal.restaurant, "name", "") if getattr(meal, "restaurant", None) else ""
        base_value = f"{restaurant_name}-{meal.name}" if restaurant_name else meal.name
        meal.slug = _build_unique_slug(Meal, base_value, "meal", exclude_pk=meal.pk)
        meal.save(update_fields=["slug"])


def remove_slugs(apps, schema_editor):
    # No-op rollback helper
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("MerchantSideApp", "0009_nutritioninfo_breakdown"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="slug",
            field=models.SlugField(blank=True, max_length=SLUG_MAX_LENGTH, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="meal",
            name="slug",
            field=models.SlugField(blank=True, max_length=SLUG_MAX_LENGTH, null=True, unique=True),
        ),
        migrations.RunPython(populate_slugs, remove_slugs),
        migrations.AlterField(
            model_name="restaurant",
            name="slug",
            field=models.SlugField(blank=True, max_length=SLUG_MAX_LENGTH, unique=True),
        ),
        migrations.AlterField(
            model_name="meal",
            name="slug",
            field=models.SlugField(blank=True, max_length=SLUG_MAX_LENGTH, unique=True),
        ),
    ]
