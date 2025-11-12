from rest_framework import serializers

from api.models import Label
from api.models.image import Image
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
            "stored_filename",
            "original_filename",
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
            "created_at",
            "updated_at"
        ]
