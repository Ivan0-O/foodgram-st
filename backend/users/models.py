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
