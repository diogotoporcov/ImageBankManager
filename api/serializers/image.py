import re
from typing import List

from django.core.exceptions import ValidationError
from rest_framework import serializers

from api.models import Label, Collection
from api.models.image import Image, MIME_TYPE_REGEX, ALLOWED_MIME_TYPES
from api.serializers import LabelSerializer


class ImageSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all(),
        required=False,
        source="labels",
        write_only=True
    )

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
            "label_ids",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "stored_filename",
            "created_at",
            "updated_at"
        ]

    def validate_mime_type(self, value: str):
        if not re.match(MIME_TYPE_REGEX, value):
            raise serializers.ValidationError("Invalid MIME type format.")

        if value not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError("MIME type not allowed.")

        return value

    def validate_label_ids(self, labels: List[Label]) -> List[Label]:
        collection: Collection = (
            self.initial_data.get("collection")
            and Collection.objects.get(id=self.initial_data["collection"])
        ) or self.instance.collection

        owner_id = collection.owner_id

        for label in labels:
            if label.owner_id != owner_id:
                raise ValidationError(
                    f"Label '{label.label}' does not belong to the same owner as the image/collection."
                )

        return labels
