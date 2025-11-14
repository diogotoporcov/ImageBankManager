from typing import List

from rest_framework import serializers


class HasLabelsSerializerMixin:
    def validate_labels(self, labels: List[str]) -> List[str]:
        if labels and len(labels) != len(set(labels)):
            raise serializers.ValidationError("Labels must have unique values.")

        return labels
