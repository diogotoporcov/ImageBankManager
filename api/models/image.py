import uuid
from typing import TYPE_CHECKING

from django.db import models


class Image(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="images",
        editable=False
    )

    collection = models.ForeignKey(
        "Collection",
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True
    )

    stored_filename = models.CharField(max_length=256, editable=False)
    filename = models.CharField(max_length=256)
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
        return f"{self.filename} ({self.owner.username})"

    def save(self, *args, **kwargs):
        self.owner = self.collection.owner

        if not self.stored_filename and self.filename:
            ext = self.mime_type.removeprefix("image/").lower()
            self.stored_filename = f"{self.id}.{ext}"

        super().save(*args, **kwargs)
