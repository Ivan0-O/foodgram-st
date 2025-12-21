import base64

from rest_framework import serializers, validators

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.urls import reverse

from djoser import serializers as djoser_serializers

from recipes.models import (Ingredient, Recipe, RecipeIngredient, Favorite,
                            ShoppingCart)
from users.models import Avatar, Subscription
from shortlinks.models import ShortLink

User = get_user_model()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(source="image")

    class Meta:
        model = Avatar
        fields = ("avatar", )

    def to_representation(self, avatar):
        return {
            "avatar":
            self.context.get("request").build_absolute_uri(avatar.image.url)
        }


class UserShortSerializer(djoser_serializers.UserCreateSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())])

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
    avatar = serializers.ImageField(source="avatar.image", read_only=True)
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

        serializer = RecipeShortSerialzier(instance=recipes,
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

    def validate_amount(self, amount):
        if amount < 1:
            raise serializers.ValidationError("Amount should be atleast 1.")

        return amount


class RecipeShortSerialzier(serializers.ModelSerializer):
    image = Base64ImageField(write_only=True, required=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

    def to_representation(self, recipe):
        data = super().to_representation(recipe)
        data["image"] = self.context.get("request").build_absolute_uri(
            recipe.image.url)
        return data

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                "Cooking time should be atleast 1.")

        return cooking_time


class ShortLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortLink
        fields = ("slug", )
        read_only_fields = ("slug", )

    def to_representation(self, link):
        abs_url = reverse("shortlink", kwargs={"slug": link.slug})
        return {
            "short-link":
            self.context.get("request").build_absolute_uri(abs_url)
        }


class RecipeSerializer(RecipeShortSerialzier):
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    ingredients = RecipeIngredientSerializer(source="recipe_ingredients",
                                             many=True,
                                             required=False)

    class Meta(RecipeShortSerialzier.Meta):
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
            id__in=ingredients_ids).values_list("id")

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
        # shady stuff
        validated_data.pop("recipe_ingredients", None)
        # create the recipe as normal
        recipe = Recipe.objects.create(**validated_data)

        try:
            self._create_ingredients(recipe,
                                     self.initial_data.get("ingredients"))
        except serializers.ValidationError as err:
            recipe.delete()
            raise err

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
