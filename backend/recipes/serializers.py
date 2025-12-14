from rest_framework import serializers

from .models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "author", "ingredients", "is_favorited",
                  "is_in_shopping_cart", "name", "image", "text",
                  "cooking_time")
        read_only_fields = ("author", )

    def get_is_favorited(self):
        return False

    def get_is_in_shopping_cart(self):
        return False
