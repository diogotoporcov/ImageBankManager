from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Type
from api.models import User, Collection


@receiver(post_save, sender=User)
def create_default_collection(
    sender: Type[User],
    instance: User,
    created: bool,
    **_kwargs
) -> None:
    _ = sender
    if created:
        Collection.objects.create(
            owner=instance,
            name="DEFAULT",
            is_default=True,
        )
