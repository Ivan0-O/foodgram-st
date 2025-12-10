from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework import validators

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            # "is_subscribed",
            # "avatar",
        )
        required_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
        )
