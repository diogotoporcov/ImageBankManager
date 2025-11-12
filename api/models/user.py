import uuid
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=128, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from django.db.models.fields.related_descriptors import RelatedManager
        from api.models.image import Image
        from api.models.collection import Collection
        from api.models.label import Label

        images: RelatedManager[Image]
        collections: RelatedManager[Collection]
        labels: RelatedManager[Label]

    def __str__(self):
        return self.username
