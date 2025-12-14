from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} ({self.measure})"


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name="recipes",
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    image = models.ImageField(
        upload_to="recipes/images/",
        null=True,
        default=None,
    )
    text = models.TextField()  # description

    ingredients = models.ManyToManyField(Ingredient,
                                         through="RecipeIngredient")

    cooking_time = models.PositiveIntegerField()  # in minutes

    def __str__(self):
        return self.name.__str__()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"{self.recipe.__str__()}: {self.ingredient.name.__str__()}"
            f"{self.amount.__str__()} {(self.ingredient
                                        .measurement_unit.__str__())}"
        )
