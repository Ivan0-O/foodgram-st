from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import (Ingredient, Recipe, RecipeIngredient, Favorite,
                     ShoppingCart)
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerialzier)
from .filters import RecipeFilter
from .pagination import PageLimitPagination

from core.permissions import IsAuthorOrReadOnly
from core.decorators import many2many_relation_action
from shortlinks.models import ShortLink
from shortlinks.serializers import ShortLinkSerializer


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get("name", "")
        return super().get_queryset().filter(name__startswith=name)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    ]
    pagination_class = PageLimitPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return self.queryset.order_by("-published")

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        serializer_class=ShortLinkSerializer,
        url_path="get-link",
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        link, _ = ShortLink.objects.get_or_create(recipe=recipe)
        serializer = self.get_serializer(link)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @many2many_relation_action(
        model=Recipe,
        rel_model=Favorite,
        usr_field="user",
        model_field="recipe",
        post_exists_message="This recipe is already in your favorites.",
        delete_missing_message="This recipe is not in your favorites.",

        # action kwargs
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerialzier,
    )
    def favorite(self, request, pk):
        pass

    @many2many_relation_action(
        model=Recipe,
        rel_model=ShoppingCart,
        usr_field="user",
        model_field="recipe",
        post_exists_message="This recipe is already in your shopping cart.",
        delete_missing_message="This recipe is not in your shopping cart.",

        # action kwargs
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerialzier,
    )
    def shopping_cart(self, request, pk):
        pass

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        # the beggining of the file is already convoluted enough
        from django.db.models import Sum
        from django.http import HttpResponse

        recipes = ShoppingCart.objects.filter(user=request.user).values("id")

        # select ingredients for all the recipes
        content = RecipeIngredient.objects.filter(recipe__in=recipes).values(
            "ingredient__name", "ingredient__measurement_unit")
        # add amount field that is the sum of all the occurences
        # of the given ingredient
        content = content.annotate(
            total_amount=Sum("amount")).order_by("ingredient__name")

        if not content:
            file = "Your shopping cart is empty."
        else:
            file = "\n".join(f"{ingredient["ingredient__name"]}: "
                             f"{int(ingredient["total_amount"])} "
                             f"({ingredient["ingredient__measurement_unit"]})"
                             for ingredient in content)

        response = HttpResponse(
            file, content_type="text/plain;charset=utf-8")
        return response
