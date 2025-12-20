from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    autocomplete_fields = ["ingredient"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "cooking_time", "favorites_count")
    search_fields = ("name", "author__username")
    list_filter = ("author", )
    inlines = [RecipeIngredientInline]

    def favorites_count(self, recipe):
        return recipe.favorited_by.count()

    favorites_count.short_description = "Кол-во добавлений в избранное"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit", )
