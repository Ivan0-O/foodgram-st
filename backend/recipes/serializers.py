from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient
from users.serializers import UserSerializer
from core.serializers import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(source="recipe_ingredients",
                                             many=True,
                                             read_only=True)
    image = Base64ImageField(write_only=True, required=True)

    class Meta:
        model = Recipe
        fields = ("id", "author", "ingredients", "is_favorited",
                  "is_in_shopping_cart", "name", "image", "text",
                  "cooking_time")

    def to_representation(self, recipe):
        data = super().to_representation(recipe)
        data["image"] = recipe.image.url
        return data

    def create(self, validated_data):
        ingredients = self.initial_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients:
            id = ingredient_data.pop("id")
            amount = ingredient_data.pop("amount")

            ingredient = Ingredient.objects.get(pk=id)
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)

        return recipe

    def get_is_favorited(self, recipe):
        return False

    def get_is_in_shopping_cart(self, recipe):
        return False
