from django.shortcuts import get_object_or_404

from rest_framework import (viewsets, mixins, permissions, pagination, filters,
                            status)
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Ingredient, Recipe, Favorite
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerialzier)
from core.permissions import IsAuthorOrReadOnly
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
    pagination_class = pagination.LimitOffsetPagination

    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_fields = ('author', )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerialzier,
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        fav, created = Favorite.objects.get_or_create(user=request.user,
                                                      recipe=recipe)

        # DELETE
        if request.method == "DELETE":
            fav.delete()
            if created:
                return Response(
                    data={"detail": "This recipe is not in your favorites."},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        # POST
        # already in favs
        if not created:
            return Response(
                data={"detail": "This recipe is already in your favorites."},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
