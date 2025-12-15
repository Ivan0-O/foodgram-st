from django.urls import path

from .views import shortlink

urlpatterns = [
        path("<slug:slug>/", shortlink, name="shortlink"),
]
