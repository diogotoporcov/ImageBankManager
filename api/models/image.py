import re
import uuid
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models

from api.models.abstract.has_label import HasLabels

MIME_TYPE_REGEX = r"(?i)^image/[a-z0-9\-+.]+$"
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


class Image(HasLabels):
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
        self.full_clean()

        self.owner = self.collection.owner

        ext = self.mime_type.removeprefix("image/").lower()
        self.stored_filename = f"{self.id}.{ext}"

        super().save(*args, **kwargs)

    def _validate_mime_type(self):
        if not re.match(MIME_TYPE_REGEX, self.mime_type):
            raise ValidationError({"mime_type": "Invalid mime type format."})

        if self.mime_type not in ALLOWED_MIME_TYPES:
            raise ValidationError({"mime_type": "Mime type not allowed."})
