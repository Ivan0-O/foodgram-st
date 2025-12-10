
from rest_framework import serializers

from .models import Ingredient, Recipe

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("name", "measurement_unit")
        # read_only_fields = ("name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ("name", "author", "image", "description", "ingredients",
                  "cook_time")
        read_only_fields = ("author", )
