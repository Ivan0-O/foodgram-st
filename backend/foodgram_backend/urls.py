from django.contrib import admin
from django.urls import include, path

from recipes.views import shortlink

urlpatterns = [
    path("admin/", admin.site.urls),
    path("s/<slug:slug>/", shortlink, name="shortlink"),
    path("api/", include("api.urls")),
]
