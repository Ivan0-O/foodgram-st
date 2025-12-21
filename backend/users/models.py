from django.contrib.auth.models import AbstractUser
from django.contrib.auth import validators
from django.db import models

from foodgram_backend.constants import (
    USER_USERNAME_MAX_LENGTH,
    USER_AVATAR_PATH,
    USER_EMAIL_MAX_LENGTH,
    USER_FIRST_NAME_MAX_LENGTH,
    USER_LAST_NAME_MAX_LENGTH,
)


# logging in is done via an email+password combination
# see TokenCreateSerializer from api.views
class User(AbstractUser):
    # make email unique
    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
    )

    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=USER_USERNAME_MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[validators.ASCIIUsernameValidator()])

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=USER_FIRST_NAME_MAX_LENGTH,
    )

    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=USER_LAST_NAME_MAX_LENGTH,
    )

    avatar = models.ImageField(verbose_name="Аватар пользователя",
                               upload_to=USER_AVATAR_PATH,
                               null=True,
                               blank=True,
                               default=None)

    class Meta(AbstractUser.Meta):
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    subscriber = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name="subscriptions",
                                   verbose_name="Подписчик")
    subscribed_to = models.ForeignKey(User,
                                      on_delete=models.CASCADE,
                                      related_name="subscribers",
                                      verbose_name="Подписан на")

    class Meta:
        unique_together = ("subscriber", "subscribed_to")

        verbose_name = "подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return (f"{self.subscriber.username} subscribed to "
                f"{self.subscribed_to.username}")
