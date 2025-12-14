from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient
from users.serializers import UserSerializer
from core.serializers import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientSerializer(many=True, read_only=True)
    image_url = serializers.ImageField(source="image", read_only=True)
    image = Base64ImageField(write_only=True, required=True)

    class Meta:
        model = Recipe
        fields = ("id", "author", "ingredients", "is_favorited",
                  "is_in_shopping_cart", "name", "image", "image_url", "text",
                  "cooking_time")
        # read_only_fields = ("is_favorited", "is_in_shopping_cart")

    def to_representation(self, recipe):
        data = super().to_representation(recipe)
        data["image"] = data.pop("image_url")
        return data

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in self.initial_data.pop("ingredients"):
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
