import uuid
from typing import TYPE_CHECKING

from django.db import models


class HasUUID(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    if TYPE_CHECKING:
        id: uuid.UUID

    class Meta:
        abstract = True
