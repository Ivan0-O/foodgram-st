from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("s/", include("shortlinks.urls")),
    path("api/", include("users.urls")),
    path("api/", include("recipes.urls")),

    # djoser
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/auth/", include("djoser.urls")),
]
