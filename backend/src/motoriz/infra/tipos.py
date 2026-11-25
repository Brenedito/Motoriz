from typing import Any
from uuid import UUID

from sqlalchemy import BINARY
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class UUIDBinario(TypeDecorator[UUID]):
    """UUID guardado como BINARY(16)."""

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value: UUID | None, dialect: Dialect) -> bytes | None:
        return None if value is None else value.bytes

    def process_result_value(self, value: Any, dialect: Dialect) -> UUID | None:
        return None if value is None else UUID(bytes=bytes(value))
