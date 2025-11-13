from rest_framework import serializers
from api.models.image import Image, MIME_TYPE_REGEX, ALLOWED_MIME_TYPES
import re


class ImageSerializer(serializers.ModelSerializer):
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
        if not re.match(MIME_TYPE_REGEX, value):
            raise serializers.ValidationError("Invalid MIME type format.")

        if value not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError("MIME type not allowed.")

        return value
