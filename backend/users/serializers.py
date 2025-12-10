from django.contrib.auth import get_user_model

from djoser import serializers as djoser_serializers

from rest_framework import serializers
from rest_framework import validators

User = get_user_model()


# Just setting a bunch of fields as required and checking email uniqueness
class UserSerializer(djoser_serializers.UserCreateSerializer):
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
            # "is_subscribed",
            # "avatar",
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
