from django.shortcuts import get_object_or_404, redirect

from .models import ShortLink


def shortlink(request, slug):
    recipe = get_object_or_404(ShortLink, slug=slug).recipe
    return redirect("recipes-detail", pk=recipe.id)
