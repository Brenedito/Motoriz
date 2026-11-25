from datetime import UTC, datetime, timedelta
from typing import Protocol


class Relogio(Protocol):
    def agora(self) -> datetime: ...


class RelogioDoSistema:
    def agora(self) -> datetime:
        return datetime.now(UTC)


class RelogioFixo:
    def __init__(self, instante: datetime) -> None:
        self._instante = instante

    def agora(self) -> datetime:
        return self._instante

    def avancar(self, delta: timedelta) -> None:
        self._instante += delta
