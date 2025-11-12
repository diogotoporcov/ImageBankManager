from typing import Iterable

from django.contrib.auth.models import AbstractBaseUser
from guardian.shortcuts import assign_perm, remove_perm

from api.models.collection import Collection
from api.models.image import Image
from api.services.permissions.enums import Permission


def share_collection_with_user(
    collection: Collection,
    user: AbstractBaseUser,
    perms: Iterable[Permission],
) -> None:
    for perm in perms:
        assign_perm(f"{perm}_collection", user, collection)

    images: Iterable[Image] = collection.images.all()
    for image in images:
        for perm in perms:
            assign_perm(f"{perm}_image", user, image)


def revoke_collection_share_from_user(
    collection: Collection,
    user: AbstractBaseUser,
    perms: Iterable[Permission],
) -> None:
    for perm in perms:
        remove_perm(f"{perm}_collection", user, collection)

    images: Iterable[Image] = collection.images.all()
    for image in images:
        for perm in perms:
            remove_perm(f"{perm}_image", user, image)
