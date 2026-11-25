from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import BINARY
from sqlalchemy.dialects.mysql import DATETIME
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


class DataHoraUTC(TypeDecorator[datetime]):
    """`datetime` com fuso no Python; DATETIME(6) em UTC no MySQL, que não guarda fuso."""

    impl = DATETIME(fsp=6)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("datetime sem fuso horário")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        return None if value is None else value.replace(tzinfo=UTC)
