from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Аватар", {"fields": ("avatar", )}), )
    search_fields = ("username", "email")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "subscribed_to")
