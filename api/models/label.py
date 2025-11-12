import uuid
from typing import TYPE_CHECKING

from django.db import models


class Label(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="labels"
    )
    label = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from django.db.models.fields.related_descriptors import RelatedManager
        from api.models.image import Image
        from api.models.collection import Collection

        images: RelatedManager[Image]
        collections: RelatedManager[Collection]

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "label"], name="unique_label_per_owner")
        ]

    def __str__(self):
        return f"{self.label} ({self.owner.username})"
