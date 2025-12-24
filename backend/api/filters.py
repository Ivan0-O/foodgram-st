from django.db.models import Q
from django_filters import FilterSet, filters
from recipes.models import Ingredient, Recipe

BOOL_CHOICES = (
    ("1", "True"),
    ("True", "True"),
    ("true", "True"),
    ("0", "False"),
    ("False", "False"),
    ("false", "False"),
)

BOOL_MAPPINGS = {
    True: [string for string, _ in BOOL_CHOICES[:3]],
    False: [string for string, _ in BOOL_CHOICES[3:]],
}


def bool_coerce(value):
    if value in BOOL_MAPPINGS[True]:
        return True
    if value in BOOL_MAPPINGS[False]:
        return False

    raise ValueError()


class RecipeFilter(FilterSet):
    is_favorited = filters.TypedChoiceFilter(
        choices=BOOL_CHOICES,
        coerce=bool_coerce,
        method="filter_is_favorited",
    )
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=BOOL_CHOICES,
        coerce=bool_coerce,
        method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author")

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset

        filter = Q(favorited_by__user=self.request.user)
        if not value:
            filter = ~filter

        return queryset.filter(filter)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset

        filter = Q(in_shopping_cart_of__user=self.request.user)
        if not value:
            filter = ~filter

        return queryset.filter(filter)


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]
