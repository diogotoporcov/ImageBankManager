from typing import List, Tuple

from api.services.permissions.enums import Permission


def model_permissions(model: str) -> List[Tuple[str, str]]:
    return [
        (f"{perm}_{model}", f"Can {perm} {model}")
        for perm
        in Permission
    ]
