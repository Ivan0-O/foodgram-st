from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64)
    measure = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.name} ({self.measure})"


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name="recipes",
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    image = models.ImageField(
        upload_to="recipes/images/",
        null=True,
        default=None,
    )
    desctiption = models.TextField()

    # ???
    # Ингредиенты — продукты для приготовления блюда по рецепту.
    # Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения.
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient")  # TODO: create RecipeIngredient

    cook_time = models.PositiveIntegerField()  # in minutes

    def __str__(self):
        return self.name.__str__()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'

