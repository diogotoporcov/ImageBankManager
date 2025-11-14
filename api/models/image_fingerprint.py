from typing import TYPE_CHECKING

from django.db import models
from pgvector.django import VectorField

from api.models.abstract import TimeStampedModel


class ImageFingerprint(TimeStampedModel):
    image = models.OneToOneField(
        "Image",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="fingerprint",
        help_text="Image to which this fingerprint data belongs."
    )

    sha256 = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hash of the image content, used for exact duplicate detection."
    )

    phash = models.BigIntegerField(
        db_index=True,
        help_text="Perceptual hash of the image, used for similarity comparison."
    )

    embedding = VectorField(
        dimensions=512,
        help_text="512-dimensional vector embedding representing the image features for similarity search."
    )

    if TYPE_CHECKING:
        from api.models.image import Image
        image: Image

    def __str__(self):
        return f"Fingerprint for {self.image.id} ({self.image})"
