from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models

from api.models.abstract import HasLabels, HasOwner, HasUUID, TimeStampedModel


class Collection(HasUUID, HasOwner, HasLabels, TimeStampedModel):
    name = models.CharField(
        max_length=64,
        help_text="Name of the collection."
    )

    is_default = models.BooleanField(
        default=False,
        editable=False,
        help_text="Indicates whether this is the user default selection. Managed by the system."
    )

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
