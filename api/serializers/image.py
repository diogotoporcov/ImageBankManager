import re

from rest_framework import serializers

from api.models.image import Image, MIME_TYPE_REGEX, ALLOWED_MIME_TYPES
from api.serializers.mixins import HasLabelsSerializerMixin


class ImageSerializer(HasLabelsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            "id",
            "filename",
            "mime_type",
            "size_bytes",
            "owner",
            "collection",
            "labels",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "stored_filename",
            "created_at",
            "updated_at",
        ]

    def validate_mime_type(self, value: str):
        value = value.lower()

        if not re.match(MIME_TYPE_REGEX, value):
            raise serializers.ValidationError("Invalid MIME type format.")

        if value not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(f"MIME type not allowed: {value}.")

        return value
