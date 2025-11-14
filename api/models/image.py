import re

from django.core.exceptions import ValidationError
from django.db import models

from api.models.abstract import HasUUID, HasOwner, TimeStampedModel
from api.models.abstract.has_labels import HasLabels

MIME_TYPE_REGEX = r"(?i)^image/[a-z0-9\-+.]+$"
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


class Image(HasUUID, HasOwner, HasLabels, TimeStampedModel):
    collection = models.ForeignKey(
        "Collection",
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True,
        help_text="Collection to which this image belongs."
    )

    stored_filename = models.CharField(
        max_length=256,
        editable=False,
        help_text="Internal filename used for storage. Managed by the system."
    )

    filename = models.CharField(
        max_length=256,
        help_text="Original filename provided by the user at upload time."
    )

    mime_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file."
    )

    size_bytes = models.BigIntegerField(
        help_text="Size of the file in bytes."
    )

    def __str__(self):
        return f"{self.filename} ({self.owner.username})"

    def clean(self):
        self.mime_type = self.mime_type.lower()
        super().clean()

    def save(self, *args, **kwargs):
        self.owner = self.collection.owner

        self.full_clean()

        ext = self.mime_type.removeprefix("image/")
        self.stored_filename = f"{self.id}.{ext}"

        super().save(*args, **kwargs)

    def _validate_mime_type(self):
        if not re.match(MIME_TYPE_REGEX, self.mime_type):
            raise ValidationError({"mime_type": "Invalid mime type format."})

        if self.mime_type not in ALLOWED_MIME_TYPES:
            raise ValidationError({"mime_type": "Mime type not allowed."})
