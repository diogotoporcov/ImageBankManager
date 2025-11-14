from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models

from api.models.abstract import HasUUID, TimeStampedModel


class User(AbstractUser, HasUUID, TimeStampedModel):
    full_name = models.CharField(max_length=128, blank=False)

    if TYPE_CHECKING:
        from django.db.models.fields.related_descriptors import RelatedManager
        from api.models.image import Image
        from api.models.collection import Collection

        images: RelatedManager[Image]
        collections: RelatedManager[Collection]

    def __str__(self):
        return self.username
