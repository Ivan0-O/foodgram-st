from django.urls import include, path

from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
]
