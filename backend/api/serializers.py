import base64

from rest_framework import serializers, validators

from django.core.files.base import ContentFile
from django.urls import reverse
from django.db import transaction

from djoser import serializers as djoser_serializers

from recipes.models import (Ingredient, Recipe, RecipeIngredient, Favorite,
                            ShoppingCart)
from users.models import User, Subscription


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar", )
        extra_kwargs = {"avatar": {"required": True}}

    def to_representation(self, user):
        if user.avatar:
            request = self.context.get("request")
            return {"avatar": request.build_absolute_uri(user.avatar.url)}
        return {"avatar": None}


class UserShortSerializer(djoser_serializers.UserCreateSerializer):

    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "password": {
                "write_only": True
            },
            "email": {
                "required": True
            },
            "username": {
                "required": True
            },
            "first_name": {
                "required": True
            },
            "last_name": {
                "required": True
            },
        }


class UserSerializer(UserShortSerializer):
    avatar = serializers.ImageField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserShortSerializer.Meta):
        fields = UserShortSerializer.Meta.fields + ("is_subscribed", "avatar")

    def get_is_subscribed(self, other_user):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False

        return Subscription.objects.filter(subscriber=request.user,
                                           subscribed_to=other_user).exists()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, other_user):
        recipes = other_user.recipes.all()
        limit = self.context.get("request").query_params.get(
            "recipes_limit", None)
        if limit is not None:
            limit = int(limit)
            recipes = recipes[:limit]

        serializer = RecipeShortSerializer(instance=recipes,
                                           many=True,
                                           context=self.context)
        return serializer.data


# Requires email+password combination instead of default username+password
class TokenCreateSerializer(djoser_serializers.TokenCreateSerializer):

    class Meta:
        fields = ("email", "password")
        extra_kwargs = {
            "email": {
                "required": True,
            },
        }

    def validate(self, attrs):
        cred_err = djoser_serializers.ValidationError(
            "Invalid credentials provided.")

        # finding the user
        try:
            # Can't use get_object_404 because the code 400 is required
            self.user = User.objects.get(email=attrs.get("email", None))
        except Exception:
            raise cred_err

        if not self.user.check_password(attrs.get("password", None)):
            raise cred_err

        # setting attrs["user"] so it would appear in serializer.validated_data
        attrs["user"] = self.user
        return attrs


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


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(write_only=True, required=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def to_representation(self, recipe):
        data = super().to_representation(recipe)
        data["image"] = self.context.get("request").build_absolute_uri(
            recipe.image.url)
        return data


class ShortLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ("slug", )
        read_only_fields = ("slug", )

    def to_representation(self, link):
        absolute_url = reverse("shortlink", kwargs={"slug": link})
        return {
            "short-link":
            self.context.get("request").build_absolute_uri(absolute_url)
        }


class RecipeSerializer(RecipeShortSerializer):
    author = UserSerializer(read_only=True)

    # Can't make these fields through queryset annotations in viewset
    # because they wouldn't show on post requests
    # which is required by the docs
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    ingredients = RecipeIngredientSerializer(source="recipe_ingredients",
                                             many=True,
                                             required=False)

    class Meta(RecipeShortSerializer.Meta):
        # redefining and not inheriting because we need to keep the specified
        # ordering (e.g. `author` goes after `id` but before `name`)
        fields = ("id", "author", "ingredients", "is_favorited",
                  "is_in_shopping_cart", "name", "image", "text",
                  "cooking_time")

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

    def _create_ingredients(self, recipe, ingredients):
        ingredients_ids = [ingredient["id"] for ingredient in ingredients]
        ingredients_amounts = [
            ingredient["amount"] for ingredient in ingredients
        ]

        if (ingredients_ids.__len__() != set(ingredients_ids).__len__()):
            raise serializers.ValidationError(
                {"ingredients": ["Ingredients cannot repeat."]})

        existing_ingredients_ids = Ingredient.objects.filter(
            id__in=ingredients_ids).values_list("id", flat=True)

        if existing_ingredients_ids.__len__() != ingredients_ids.__len__():
            missing_id = (id for id in ingredients_ids
                          if id not in existing_ingredients_ids).__next__()
            raise serializers.ValidationError(
                {"detail": f"Ingredient with id {missing_id} does not exist."})

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=id,
                amount=amount,
            ) for id, amount in zip(ingredients_ids, ingredients_amounts)
        ])

    def create(self, validated_data):
        # we handle it ourselves
        validated_data.pop("recipe_ingredients", None)

        # transaction will revert the creation if a validation error occurs
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)

            self._create_ingredients(recipe,
                                     self.initial_data.get("ingredients"))

        return recipe

    def update(self, recipe, validated_data):
        # we handle it ourselves
        validated_data.pop("recipe_ingredients", None)

        # update ingredients only if they were provided
        ingredients = self.initial_data.get("ingredients")
        if ingredients is not None:
            # delete the old ones
            RecipeIngredient.objects.filter(recipe=recipe).delete()

            self._create_ingredients(recipe, ingredients)

        # update all the other fields as normal
        recipe = super().update(recipe, validated_data)

        return recipe

    def _user_recipe_getter_mixin(self, recipe, model):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return model.objects.filter(user=user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        return self._user_recipe_getter_mixin(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self._user_recipe_getter_mixin(recipe, ShoppingCart)
