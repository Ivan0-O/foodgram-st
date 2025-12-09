from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView

from rest_framework import routers

from recipes.views import IngredientViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register(r"recipes", RecipeViewSet)
router.register(r"ingredients", IngredientViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # djoser
    path("api/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("redoc/",
             TemplateView.as_view(template_name="redoc.html"),
             name="redoc"),
    ]
