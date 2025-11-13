from rest_framework import serializers

from api.models import Label, Image
from api.models.collection import Collection
from api.serializers.label import LabelSerializer


class CollectionSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all(),
        required=False,
        source="labels",
        write_only=True
    )

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
            "label_ids",
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
