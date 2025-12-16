from django_filters import FilterSet
from django_filters import filters

from django.db.models import Q

from .models import Recipe

BOOL = (
    ("1", "True"),
    ("True", "True"),
    ("true", "True"),
    ("0", "False"),
    ("False", "False"),
    ("false", "False"),
)

BOOL_DICT = {
    True: [v for v, _ in BOOL[:3]],
    False: [v for v, _ in BOOL[3:]],
}


# Need to convert the value ourselves because default
# BooleanFilter only expects True/False and does not
# want to call my filter functions when recieves 1/0
def bool_coerce(value):
    if value in BOOL_DICT[True]:
        return True
    if value in BOOL_DICT[False]:
        return False

    # django_filters will print that this choice is not allowed
    raise ValueError()


class RecipeFilter(FilterSet):
    is_favorited = filters.TypedChoiceFilter(
        choices=BOOL,
        coerce=bool_coerce,
        method="filter_is_favorited",
    )
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=BOOL, coerce=bool_coerce, method="filter_is_in_shopping_cart")

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
