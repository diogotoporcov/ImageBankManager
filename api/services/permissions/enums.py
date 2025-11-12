from enum import StrEnum


class Permission(StrEnum):
    ADD = "add"
    CHANGE = "change"
    DELETE = "delete"
    VIEW = "view"
