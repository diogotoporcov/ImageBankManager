from rest_framework import serializers

from api.models.collection import Collection
from api.serializers.mixins import LabelValidationMixin


class CollectionSerializer(LabelValidationMixin, serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
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
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "is_default",
            "images",
            "created_at",
            "updated_at"
        ]