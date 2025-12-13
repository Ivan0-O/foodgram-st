import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from djoser import serializers as djoser_serializers

from rest_framework import serializers
from rest_framework import validators

from .models import Avatar, Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    # url of the image: "http://foodgram.example.org/media/users/image.png"
    avatar = serializers.ImageField(source="image", read_only=True)

    # base64 representation of the image: "data:image/png;base64,xyz"
    image = Base64ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Avatar
        fields = ("avatar", "image")


class UserSerializer(djoser_serializers.UserCreateSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())])
    avatar = serializers.ImageField(source="avatar.image", read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
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

    def get_is_subscribed(self, sub_to):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False

        return Subscription.objects.filter(subscriber=request.user,
                                           subscribed_to=sub_to).exists()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, sub_to):
        pass

    def get_recipes_count(self, sub_to):
        pass


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
