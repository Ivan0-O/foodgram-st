from django.contrib.auth import get_user_model

from djoser import serializers as djoser_serializers

from rest_framework import serializers
from rest_framework import validators

from .models import Avatar, Subscription
from recipes.models import Recipe
from core.serializers import Base64ImageField

User = get_user_model()


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
    # local import to resolve circular dependency
    from recipes.serializers import RecipeShortSerialzier

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, other_user):
        recipes = other_user.recipes.all()
        limit = self.context.get("request").query_params.get(
            "recipes_limit", None)
        if limit is not None:
            limit = int(limit)
            recipes = recipes[:limit]

        serializer = self.RecipeShortSerialzier(instance=recipes,
                                                many=True,
                                                context=self.context)
        return serializer.data

    def get_recipes_count(self, other_user):
        return other_user.recipes.count()


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
            self.user = User.objects.get(email=attrs.get("email", None))
        except Exception:
            raise cred_err

        if not self.user.check_password(attrs.get("password", None)):
            raise cred_err

        # setting attrs["user"] so it would appear in serializer.validated_data
        attrs["user"] = self.user
        return attrs
