from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.http import HttpResponse

from djoser import views as djoser_views

from rest_framework import viewsets, mixins, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from users.models import Avatar, Subscription
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Favorite,
                            ShoppingCart)

from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerialzier, AvatarSerializer,
                          UserWithRecipesSerializer, ShortLinkSerializer)
from .filters import RecipeFilter
from .pagination import PageLimitPagination

from .permissions import IsAuthorOrReadOnly
from shortlinks.models import ShortLink


User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = (
        User.objects
        .all()
        .order_by("username")
        .annotate(recipes_count=Count("recipes"))
    )
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
            avatar = get_object_or_404(Avatar, user=user)
            avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        sub_to = (
            self.get_queryset()
            .filter(subscribers__subscriber=request.user)
        )
        # serialize only a single page
        page = self.paginate_queryset(sub_to)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    # TODO: extract
    @action(
        detail=True,
        methods=["post", "delete"],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id):
        # not allowing subscribing to yourself
        id = int(id)
        if id == request.user.id:
            return Response(data={"detail": "Cannot subscribe to yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        sub_to = get_object_or_404(self.get_queryset(), pk=id)
        sub, created = Subscription.objects.get_or_create(
            subscriber=request.user, subscribed_to=sub_to)

        # DELETE
        if request.method == "DELETE":
            sub.delete()
            if created:
                return Response(
                    data={"detail": "Not subscribed to that user."},
                    status=status.HTTP_400_BAD_REQUEST)
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

    # @action(
    #     detail=True,
    #     methods=["post", "delete"],
    #     serializer_class=UserWithRecipesSerializer,
    # )
    # def subscribe(self, request, id):
    #     # not allowing subscribing to yourself
    #     id = int(id)
    #     if id == request.user.id:
    #         return Response(data={"detail": "Cannot subscribe to yourself."},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #
    #     return _many2many_relation(
    #         self, request, User, Subscription, id,
    #         user_field="subscriber",
    #         model_field="subscribed_to",
    #         post_exists_message="Not subscribed to that user.",
    #         delete_missing_message="Not subscribed to that user.",
    #     )


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get("name", "")
        return super().get_queryset().filter(name__istartswith=name)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    ]
    pagination_class = PageLimitPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return self.queryset.order_by("-published")

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        serializer_class=ShortLinkSerializer,
        url_path="get-link",
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        link, _ = ShortLink.objects.get_or_create(recipe=recipe)
        serializer = self.get_serializer(link)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # @action(
    #     detail=True,
    #     methods=["post", "delete"],
    #     permission_classes=[permissions.IsAuthenticated],
    #     serializer_class=RecipeShortSerialzier,
    # )
    # def favorite(self, request, pk):
    #     return _many2many_relation(
    #         self, request, Recipe, Favorite, pk,
    #         user_field="user",
    #         model_field="recipe",
    #         post_exists_message=(
    #             "This recipe is already in your favorites."),
    #         delete_missing_message=(
    #             "This recipe is not in your favorites."),
    #     )

    # TODO: extract
    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerialzier,
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        fav, created = Favorite.objects.get_or_create(user=request.user,
                                                      recipe=recipe)

        # DELETE
        if request.method == "DELETE":
            fav.delete()
            if created:
                return Response(
                    data={"detail": "This recipe is not in your favorites."},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        # POST
        # already in favs
        if not created:
            return Response(
                data={"detail": "This recipe is already in your favorites."},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    # TODO: extract
    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerialzier,
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        cart, created = ShoppingCart.objects.get_or_create(user=request.user,
                                                           recipe=recipe)

        # DELETE
        if request.method == "DELETE":
            cart.delete()
            if created:
                return Response(data={
                    "detail":
                    "This recipe is not in your shopping cart."
                },
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)

        # POST
        # already in shopping cart
        if not created:
            return Response(data={
                "detail":
                "This recipe is already in your shopping cart."
            },
                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    # @action(
    #     detail=True,
    #     methods=["post", "delete"],
    #     permission_classes=[permissions.IsAuthenticated],
    #     serializer_class=RecipeShortSerialzier,
    # )
    # def shopping_cart(self, request, pk):
    #     return _many2many_relation(
    #         self, request, Recipe, ShoppingCart, pk,
    #         user_field="user",
    #         model_field="recipe",
    #         post_exists_message="This recipe is already in your shopping cart.",
    #         delete_missing_message="This recipe is not in your shopping cart.",
    #     )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        recipes = ShoppingCart.objects.filter(
            user=request.user).values("recipe")

        # select ingredients for all the recipes
        content = RecipeIngredient.objects.filter(recipe__in=recipes).values(
            "ingredient__name", "ingredient__measurement_unit")
        # add amount field that is the sum of all the occurences
        # of the given ingredient
        content = content.annotate(
            total_amount=Sum("amount")).order_by("ingredient__name")

        if not content:
            file = "Your shopping cart is empty."
        else:
            file = "\n".join(f"{ingredient["ingredient__name"]}: "
                             f"{int(ingredient["total_amount"])} "
                             f"({ingredient["ingredient__measurement_unit"]})"
                             for ingredient in content)

        response = HttpResponse(file, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = (
            "attachment; filename=\"shopping_list.txt\"")
        return response
