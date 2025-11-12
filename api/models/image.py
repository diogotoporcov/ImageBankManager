import uuid
from typing import TYPE_CHECKING

from django.db import models

from api.services.permissions.utils import model_permissions


class Image(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="images"
    )

    collection = models.ForeignKey(
        "Collection",
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True
    )

    stored_filename = models.CharField(max_length=256)
    original_filename = models.CharField(max_length=256)
    mime_type = models.CharField(max_length=100)
    size_bytes = models.BigIntegerField()

    labels = models.ManyToManyField("Label", related_name="images", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from api.models.image_fingerprint import ImageFingerprint
        from api.models.image_duplicate import ImageDuplicate
        from django.db.models.fields.related_descriptors import RelatedManager

        fingerprint: ImageFingerprint
        duplicate_record: ImageDuplicate
        duplicates: RelatedManager[ImageDuplicate]

    def __str__(self):
        return f"{self.original_filename} ({self.owner.username})"
