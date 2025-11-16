from typing import TYPE_CHECKING, List

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from ImageBankManager.config import config


class HasLabels(models.Model):
    labels = ArrayField(
        base_field=models.CharField(max_length=64),
        default=list,
        blank=True,
        size=config.MAX_LABELS,
        help_text=f"List of labels associated with this item. Supports up to {config.MAX_LABELS} entries.",
    )

    if TYPE_CHECKING:
        labels: List[str]

    class Meta:
        abstract = True

    def clean(self):
        self._validate_labels()
        super().clean()

    def _validate_labels(self):
        if not isinstance(self.labels, list) or not all(isinstance(label, str) for label in self.labels):
            raise ValidationError("Labels must be a list of strings.")

        if len(self.labels) != len(set(self.labels)):
            raise ValidationError("Labels must be unique.")
