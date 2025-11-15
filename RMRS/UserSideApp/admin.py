from django.contrib import admin
from .models import AppUser

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "full_name", "created_at", "updated_at")
    search_fields = ("username", "email", "full_name")
    ordering = ("-created_at",)

admin.site.register(AppUser, UserAdmin)