from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Аватар", {"fields": ("avatar", )}), )

# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ("name", "measurement_unit")
#     search_fields = ("name", "measurement_unit")
#     list_filter = ("measurement_unit", )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "subscribed_to")
