from typing import TYPE_CHECKING

from django.db import models
from pgvector.django import VectorField


class ImageFingerprint(models.Model):
    image = models.OneToOneField(
        "Image",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="fingerprint"
    )

    sha256 = models.CharField(max_length=64, db_index=True)
    phash = models.BigIntegerField(db_index=True)
    embedding = VectorField(dimensions=512)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from api.models.image import Image
        image: Image

    def __str__(self):
        return f"Fingerprint for {self.image.id} ({self.image})"
