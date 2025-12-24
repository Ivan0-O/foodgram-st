from django.contrib import admin
from django.urls import include, path
from recipes.views import short_link

urlpatterns = [
    path("admin/", admin.site.urls),
    path("s/<slug:slug>/", short_link, name="short_link"),
    path("api/", include("api.urls")),
]
