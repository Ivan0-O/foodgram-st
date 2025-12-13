from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Avatar(models.Model):
    user = models.OneToOneField(User,
                                related_name="avatar",
                                on_delete=models.CASCADE)
    image = models.ImageField(upload_to="users/", null=True, default=None)

    def __str__(self):
        return f"{self.user.username.__str__()} avatar"


class Subscription(models.Model):
    subscriber = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   related_name="subscriptions")
    subscribed_to = models.ForeignKey(User,
                                      on_delete=models.CASCADE,
                                      related_name="subscribers")

    class Meta:
        unique_together = ("subscriber", "subscribed_to")

    def __str__(self):
        return (f"{self.subscriber.username.__str__()} subscribed to "
                f"{self.subscribed_to.username.__str__()}")
