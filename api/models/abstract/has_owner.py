from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models


class HasOwner(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    if TYPE_CHECKING:
        from api.models import User
        owner: User

    class Meta:
        abstract = True
