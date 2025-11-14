import uuid
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models

from api.models.abstract.has_label import HasLabels


class Collection(HasLabels):
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
    is_default = models.BooleanField(default=False, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from api.models.image import Image
        from django.db.models.fields.related_descriptors import RelatedManager
        images: RelatedManager[Image]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner"],
                condition=models.Q(is_default=True),
                name="unique_default_collection_per_user"
            )
        ]

    def clean(self):
        self._validate_is_default_unchanged()
        super().clean()

    def delete(self, *args, **kwargs):
        if self.is_default:
            raise ValidationError("Cannot delete the default collection.")

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def _validate_is_default_unchanged(self):
        if self._state.adding:
            return

        old = Collection.objects.get(pk=self.pk)
        if old.is_default != self.is_default:
            raise ValidationError("You cannot modify is_default.")
