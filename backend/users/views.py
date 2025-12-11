from django.contrib.auth import get_user_model

from rest_framework import permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend

from djoser import views as djoser_views

from .models import Avatar
from .serializers import AvatarSerializer

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

    @action(detail=False, methods=["put", "delete"], url_path="me/avatar")
    def avatar(self, request):
        user = request.user

        if request.method == "PUT":
            avatar, created = Avatar.objects.get_or_create(user=user)

            data = request.data
            # moving from "avatar" to "image" because of the naming gimmick
            # in the AvatarSerializer
            data["image"] = data.pop("avatar")

            serializer = AvatarSerializer(avatar, data=data, partial=True)
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK
                            if not created else status.HTTP_201_CREATED)

        # generic delete thing
        if request.method == "DELETE":
            try:
                avatar = user.avatar
                avatar.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except Avatar.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
