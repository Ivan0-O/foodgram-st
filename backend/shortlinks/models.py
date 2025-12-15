import random
import string

from django.db import models

from recipes.models import Recipe


def create_slug():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


class ShortLink(models.Model):
    recipe = models.ForeignKey(Recipe,
                               related_name="short_link",
                               on_delete=models.CASCADE)
    slug = models.SlugField(max_length=8,
                            unique=True,
                            default=create_slug,
                            editable=False)

    def __str__(self):
        return self.slug.__str__()
