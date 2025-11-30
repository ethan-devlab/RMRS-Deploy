from django.contrib import admin

from .models import Meal, MerchantAccount, Restaurant, Tag


class MerchantAccountInline(admin.StackedInline):
	model = MerchantAccount
	can_delete = False
	extra = 0
	readonly_fields = ("email", "created_at", "updated_at")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
	list_display = (
		"name",
		"city",
		"district",
		"cuisine_type",
		"price_range",
		"latitude",
		"longitude",
		"is_active",
		"updated_at",
	)
	list_filter = ("is_active", "price_range", "city")
	search_fields = ("name", "city", "district", "cuisine_type")
	inlines = [MerchantAccountInline]
	readonly_fields = ("created_at", "updated_at")


@admin.register(MerchantAccount)
class MerchantAccountAdmin(admin.ModelAdmin):
	list_display = ("merchant_name", "email", "restaurant", "created_at", "updated_at")
	search_fields = ("merchant_name", "email", "restaurant__name")
	list_select_related = ("restaurant",)
	autocomplete_fields = ("restaurant",)
	readonly_fields = ("created_at", "updated_at")


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
	list_display = ("name", "restaurant", "category", "price", "is_available")
	list_filter = ("is_available", "category", "restaurant")
	search_fields = ("name", "description", "restaurant__name")
	list_select_related = ("restaurant",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	search_fields = ("name",)
