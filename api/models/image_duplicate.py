from typing import TYPE_CHECKING

from django.db import models

from api.models.abstract import TimeStampedModel


class ImageDuplicate(TimeStampedModel):
    image = models.OneToOneField(
        "Image",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="duplicate_record"
    )

    original_image = models.ForeignKey(
        "Image",
        on_delete=models.CASCADE,
        related_name="duplicates"
    )

    if TYPE_CHECKING:
        from api.models.image import Image
        image: Image
        original_image: Image

    def __str__(self):
        return f"Duplicate of {self.original_image} (image {self.image.id})"
