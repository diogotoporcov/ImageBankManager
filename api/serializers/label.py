from rest_framework import serializers
from api.models.label import Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            "id",
            "label",
            "owner",
            "created_at",
            "modified_at"
        ]

        read_only_fields = [
            "id",
            "created_at",
            "modified_at"
        ]
