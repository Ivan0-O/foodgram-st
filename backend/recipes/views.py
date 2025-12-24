from django.shortcuts import get_object_or_404, redirect

from .models import Recipe


def short_link(request, slug):
    recipe = get_object_or_404(Recipe, short_link=slug)
    return redirect(f"/recipes/{recipe.id}/")
