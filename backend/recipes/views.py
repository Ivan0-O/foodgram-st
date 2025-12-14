from rest_framework import viewsets, mixins, permissions

from .models import Ingredient, Recipe
from .serializers import IngredientSerializer, RecipeSerializer


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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
