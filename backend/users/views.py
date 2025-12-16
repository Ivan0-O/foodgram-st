from django.contrib.auth import get_user_model

from rest_framework import permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from djoser import views as djoser_views

from .models import Avatar, Subscription
from .serializers import AvatarSerializer, UserWithRecipesSerializer
from core.decorators import many2many_relation_action

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all().order_by("username")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = pagination.LimitOffsetPagination

    @action(
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        return super().me(request)

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
        serializer_class=AvatarSerializer,
    )
    def avatar(self, request):
        user = request.user

        # DELETE
        # generic delete thing
        if request.method == "DELETE":
            try:
                avatar = user.avatar
                avatar.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except Avatar.DoesNotExist:
                return Response(data={"detail": "You do not have an avatar."},
                                status=status.HTTP_404_NOT_FOUND)

        # POST
        avatar, created = Avatar.objects.get_or_create(user=user)

        serializer = self.get_serializer(avatar, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        serializer_class=UserWithRecipesSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        sub_to = User.objects.filter(subscribers__subscriber=request.user)
        # serialize only a single page
        page = self.paginate_queryset(sub_to)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    @many2many_relation_action(
        model=User,
        rel_model=Subscription,
        usr_field="subscriber",
        model_field="subscribed_to",
        post_exists_message="Not subscribed to that user.",
        delete_missing_message="Not subscribed to that user.",

        # action kwargs
        methods=["post", "delete"],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id):
        # not allowing subscribing to yourself
        id = int(id)
        if id == request.user.id:
            return Response(data={"detail": "Cannot subscribe to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)
