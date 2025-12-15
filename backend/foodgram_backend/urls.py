from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("s/", include("shortlinks.urls")),
    path("api/", include("users.urls")),
    path("api/", include("recipes.urls")),

    # djoser
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/auth/", include("djoser.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("api/docs/",
             TemplateView.as_view(template_name="redoc.html"),
             name="redoc"),
    ]
