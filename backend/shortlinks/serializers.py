from django.urls import reverse

from rest_framework import serializers

from .models import ShortLink


class ShortLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortLink
        fields = ("slug", )
        read_only_fields = ("slug", )

    def to_representation(self, link):
        abs_url = reverse("shortlink", kwargs={"slug": link.slug})
        return {
            "short-link":
            self.context.get("request").build_absolute_uri(abs_url)
        }
