import uuid
from typing import TYPE_CHECKING

from django.db import models


class HasUUID(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=f"A UUID string identifying this item."
    )

    if TYPE_CHECKING:
        id: uuid.UUID

    class Meta:
        abstract = True
