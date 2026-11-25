import uuid

from uuid_utils.compat import uuid7


def novo_id() -> uuid.UUID:
    return uuid7()
