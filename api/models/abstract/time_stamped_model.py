from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created. Managed by the system."
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated. Managed by the system."
    )

    class Meta:
        abstract = True
