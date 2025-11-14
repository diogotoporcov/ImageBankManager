from django.core.exceptions import ValidationError
from rest_framework import serializers

from api.models import Image
from api.models.collection import Collection


class CollectionSerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    image_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Image.objects.all(),
        required=False,
        source="images",
        write_only=True
    )

    class Meta:
        model = Collection
        fields = [
            "id",
            "name",
            "is_default",
            "owner",
            "labels",
            "images",
            "image_ids",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "is_default",
            "created_at",
            "updated_at"
        ]

    def validate_labels(self, labels):
        if labels and len(labels) != len(set(labels)):
            raise ValidationError("Labels must be have unique values.")

        return labels
