from functools import wraps

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action


def many2many_relation_action(
    model,
    rel_model,
    *,
    usr_field,
    model_field,
    post_exists_message,
    delete_missing_message,
    **action_kwargs,
):

    def decorator(func):

        @action(detail=True, **action_kwargs)
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            pk = kwargs.get("pk")
            if pk is None:
                pk = kwargs.get("id")

            # let user view it run first
            response = func(self, request, *args, **kwargs)
            if response is not None:
                return response

            model_obj = get_object_or_404(model, pk=pk)
            model_kwargs = {usr_field: request.user, model_field: model_obj}
            rel_obj, created = rel_model.objects.get_or_create(**model_kwargs)

            # DELETE
            if request.method == "DELETE":
                rel_obj.delete()
                # no such relation found
                if created:
                    return Response(
                        data={"detail": delete_missing_message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return Response(status=status.HTTP_204_NO_CONTENT)

            # POST
            # already exists
            if not created:
                return Response(
                    data={"detail": post_exists_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(model_obj)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        return wrapper

    return decorator
