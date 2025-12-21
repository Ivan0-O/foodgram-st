from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("s/", include("shortlinks.urls")),
    path("api/", include("api.urls")),
]
