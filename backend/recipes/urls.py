from django.urls import include, path

from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register(r"recipes", RecipeViewSet)
router.register(r"ingredients", IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
