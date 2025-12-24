from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart)
from rest_framework import mixins, pagination, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, BaseRelationshipSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, SelfSubscriptionValidator,
                          ShortLinkSerializer, UserWithRecipesSerializer)


def _handle_relationship_action(view,
                                request,
                                relationship_model,
                                user_object,
                                target_object,
                                user_field_name,
                                target_field_name,
                                delete_not_found_message,
                                post_exists_message):
    # Get or create the relationship object
    filter_kwargs = {user_field_name: user_object,
                     target_field_name: target_object}
    relationship_object = relationship_model.objects.filter(**filter_kwargs)

    # DELETE
    if request.method == "DELETE":
        # If the object was just created, it means it didn't exist before
        if not relationship_object.exists():
            # not using get_object_or_404 because code 400
            # is required by the docs
            return Response(
                data={"detail": delete_not_found_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        relationship_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # POST
    # check if the relationship already exists
    if relationship_object.exists():
        return Response(
            data={"detail": post_exists_message},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = BaseRelationshipSerializer(
        data={},
        context={
            "model_class": relationship_model,
            "user": user_object,
            "target": target_object,
            "user_field": user_field_name,
            "target_field": target_field_name,
            "request": request
        }
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    serializer = view.get_serializer(target_object)
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(djoser_views.UserViewSet):
    queryset = (
        User.objects
        .annotate(recipes_count=Count("recipes"))
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = pagination.LimitOffsetPagination

    # setting the permissions
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

        # PUT
        if request.method == "PUT":
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # DELETE
        if not user.avatar:
            return Response(
                {"detail": "You do not have an avatar."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        serializer_class=UserWithRecipesSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        subscribed_to = (
            self.get_queryset()
            .filter(subscribers__subscriber=request.user)
        )
        # serialize only a single page
        page = self.paginate_queryset(subscribed_to)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id):
        validator = SelfSubscriptionValidator(
            data={"user_id": id},
            context={"request": request}
        )
        validator.is_valid(raise_exception=True)

        subscribe_to = get_object_or_404(self.get_queryset(), pk=id)

        return _handle_relationship_action(
            self,
            request,
            Subscription,
            request.user,
            subscribe_to,
            "subscriber",
            "subscribed_to",
            "Not subscribed to that user.",
            "You are already subscribed to that user.",
        )


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("author").prefetch_related(
        "recipe_ingredients",
        "recipe_ingredients__ingredient"
    )
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    ]
    pagination_class = PageLimitPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        serializer_class=ShortLinkSerializer,
        url_path="get-link",
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(recipe.short_link)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerializer,
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        return _handle_relationship_action(
            self,
            request,
            Favorite,
            request.user,
            recipe,
            "user",
            "recipe",
            "This recipe is not in your favorites.",
            "This recipe is already in your favorites.",
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=RecipeShortSerializer,
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        return _handle_relationship_action(
            self,
            request,
            ShoppingCart,
            request.user,
            recipe,
            "user",
            "recipe",
            "This recipe is not in your shopping cart.",
            "This recipe is already in your shopping cart.",
        )

    def _create_shopping_list_file(self, user):
        recipes = (
            ShoppingCart.objects
            .filter(user=user)
            .values("recipe")
        )

        # select ingredients for all the recipes
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in=recipes)
            .values("ingredient__name", "ingredient__measurement_unit")
        )
        # add amount field that is the sum of all the occurences
        # of the given ingredient
        ingredients = ingredients.annotate(
            total_amount=Sum("amount"))

        if not ingredients.exists():
            file = "Your shopping cart is empty."
        else:
            file = "\n".join(f"{ingredient["ingredient__name"]}: "
                             f"{int(ingredient["total_amount"])} "
                             f"({ingredient["ingredient__measurement_unit"]})"
                             for ingredient in ingredients)
        return file

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        file = self._create_shopping_list_file(request.user)
        response = HttpResponse(file, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = (
            "attachment; filename=\"shopping_list.txt\"")
        return response
