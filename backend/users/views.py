from django.contrib.auth import get_user_model

from rest_framework import permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

# from rest_framework import filters
# from django_filters.rest_framework import DjangoFilterBackend

from djoser import views as djoser_views

from .models import Avatar, Subscription
from .serializers import AvatarSerializer, UserWithRecipesSerializer

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

        data = request.data
        # moving from "avatar" to "image" because of the naming gimmick
        # in the AvatarSerializer
        try:
            data["image"] = data.pop("avatar")
        except KeyError:
            return Response(data={"avatar": "This field is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(avatar, data=data)
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

    @action(
        detail=True,
        methods=["post", "delete"],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id):
        # not allowing subscribing to yourself
        if id == request.user.id:
            return Response(data={"detail": "Cannot subscribe to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        sub_to = get_object_or_404(User, pk=id)
        sub, created = Subscription.objects.get_or_create(
            subscriber=request.user, subscribed_to=sub_to)

        # DELETE
        if request.method == "DELETE":
            sub.delete()
            if created:
                return Response(
                    data={"detail": "Not subscribed to that user."},
                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        # POST
        # already subscribed
        if not created:
            return Response(
                data={"detail": "You are already subscribed to that user."},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(sub_to)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
