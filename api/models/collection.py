import uuid
from typing import TYPE_CHECKING

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models


class Collection(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="collections"
    )

    name = models.CharField(max_length=64)
    is_default = models.BooleanField(default=False)

    labels = ArrayField(
        base_field=models.CharField(max_length=64),
        default=list,
        blank=True,
        size=16
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from api.models.image import Image
        from django.db.models.fields.related_descriptors import RelatedManager
        images: RelatedManager[Image]

    def clean(self):
        self._validate_self()
        self._validate_labels()

    def delete(self, *args, **kwargs):
        if self.is_default:
            raise ValidationError("Cannot delete the default collection.")

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            old = Collection.objects.filter(pk=self.pk).first()
            if old and not old.is_default and self.is_default:
                raise ValidationError("Cannot update a collection to is_default=True.")

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def _validate_self(self):
        if self.is_default:
            existing = Collection.objects.filter(owner=self.owner, is_default=True)
            if self.pk:
                existing = existing.exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError("User already has a default collection.")

    def _validate_labels(self):
        if not isinstance(self.labels, list) or not all(isinstance(label, str) for label in self.labels):
            raise ValidationError("Labels must be a list of strings.")

        if len(self.labels) != len(set(self.labels)):
            raise ValidationError("Labels must be unique.")