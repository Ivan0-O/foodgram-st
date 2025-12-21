import random
import string

from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from foodgram_backend.constants import (INGREDIENT_NAME_MAX_LENGTH,
                                        INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
                                        RECIPE_NAME_MAX_LENGTH,
                                        RECIPE_IMAGE_UPLOAD_PATH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH,
                            verbose_name="Название")
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения")

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


def create_slug():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name="recipes",
                               on_delete=models.CASCADE,
                               verbose_name="Автор")
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH,
                            verbose_name="Название")
    image = models.ImageField(
        upload_to=RECIPE_IMAGE_UPLOAD_PATH,
        null=True,
        default=None,
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Описание")

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[validators.MinValueValidator(1)])

    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    short_link = models.SlugField(max_length=8,
                                  unique=True,
                                  default=create_slug,
                                  editable=False)

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               related_name="recipe_ingredients",
                               on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   related_name="recipe_ingredients",
                                   on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[validators.MinValueValidator(1)])

    def __str__(self):
        return (f"{self.recipe}: {self.ingredient.name} "
                f"{self.amount} {(self.ingredient.measurement_unit)}")


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="favorites")
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="favorited_by")

    class Meta:
        unique_together = ("user", "recipe")

    def __str__(self):
        return (f"{self.user.username} favorites "
                f"{self.recipe}")


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="shopping_cart")
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="in_shopping_cart_of")

    class Meta:
        unique_together = ("user", "recipe")

    def __str__(self):
        return (f"{self.recipe} is in shopping cart of "
                f"{self.user.username}")
