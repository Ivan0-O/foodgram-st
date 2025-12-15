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

    def validate_amount(self, amount):
        if amount < 1:
            raise serializers.ValidationError("Amount should be atleast 1.")

        return amount


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(source="recipe_ingredients",
                                             many=True,
                                             required=False)
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

    def validate(self, recipe):
        # `ingredients` is being mapped to `recipe_ingredients`
        ingredients = recipe.get("recipe_ingredients")
        if ingredients is None:
            raise serializers.ValidationError(
                {"ingredients": ["This field is required."]})

        if ingredients.__len__() == 0:
            raise serializers.ValidationError(
                {"ingredients": ["Ingredients cannot be empty."]})

        return super().validate(recipe)

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                "Cooking time should be atleast 1.")

        return cooking_time

    def _push_ingredients(self, recipe, ingredients):
        for ingredient_data in ingredients:
            id = ingredient_data.get("id")
            amount = ingredient_data.get("amount")

            try:
                ingredient = Ingredient.objects.get(pk=id)

            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {"detail": f"Ingredient with id {id} does not exist."})

            # checking for duplicates
            if RecipeIngredient.objects.filter(recipe=recipe,
                                               ingredient=ingredient).exists():
                raise serializers.ValidationError(
                    {"ingredients": ["Ingredients cannot repeat."]})

            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient,
                                            amount=amount)

    def create(self, validated_data):
        # we handle it ourselves
        # shady stuff
        validated_data.pop("recipe_ingredients", None)
        # create the recipe as normal
        recipe = Recipe.objects.create(**validated_data)

        self._push_ingredients(recipe, self.initial_data.get("ingredients"))

        return recipe

    def update(self, recipe, validated_data):
        # we handle it ourselves
        validated_data.pop("recipe_ingredients", None)
        # update all the other fields as normal
        recipe = super().update(recipe, validated_data)

        # update ingredients only if they were provided
        ingredients = self.initial_data.get("ingredients")
        if ingredients is not None:
            # delete the old ones
            RecipeIngredient.objects.filter(recipe=recipe).delete()

            self._push_ingredients(recipe, ingredients)

        return recipe

    def get_is_favorited(self, recipe):
        return False

    def get_is_in_shopping_cart(self, recipe):
        return False
