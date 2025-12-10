from django.contrib.auth import get_user_model

from rest_framework import permissions

from djoser import views as djoser_views

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
