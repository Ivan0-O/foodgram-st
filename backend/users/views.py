from django.contrib.auth import get_user_model

from rest_framework import permissions, pagination

# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend

from djoser import views as djoser_views


User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    pagination_class = pagination.LimitOffsetPagination

    # NOT NEEDED NOW. For reference only
    # filter_backends = [DjangoFilterBackend,
    #                    filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ("color", "birth_year")
    # search_fields = ("$name", "owner__username")
    # ordering_fields = ("name", "birth_year")

    def get_permissions(self):
        # Refuse if an anonymous user tries to get the /users/me/
        if self.action == "me":
            return [permissions.IsAuthenticated()]

        # Otherwise use the permission_classes default
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.all().order_by("username")
