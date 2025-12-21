from django.urls import include, path

from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),

    # djoser
    path("auth/", include("djoser.urls.authtoken")),
    path("auth/", include("djoser.urls")),
]
