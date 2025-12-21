from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # make email unique
    email = models.EmailField(unique=True, max_length=254)
    avatar = models.ImageField(verbose_name="Аватар",
                               upload_to="users/",
                               null=True,
                               blank=True,
                               default=None)

    class Meta(AbstractUser.Meta):
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"


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
