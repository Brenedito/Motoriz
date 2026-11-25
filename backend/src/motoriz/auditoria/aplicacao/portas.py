from collections.abc import Mapping
from typing import Protocol
from uuid import UUID

from motoriz.auditoria.dominio.registro import RegistroDeAcao
from motoriz.compartilhado.contexto import Ator


class RegistradorDeAcoes(Protocol):
    def registrar(
        self,
        ator: Ator,
        acao: str,
        entidade: str,
        entidade_id: UUID,
        *,
        antes: Mapping[str, object] | None = None,
        depois: Mapping[str, object] | None = None,
        campos_pessoais: frozenset[str] = frozenset(),
    ) -> None: ...


class RepositorioDeRegistros(Protocol):
    def listar(self, conta_id: UUID, entidade: str, entidade_id: UUID) -> list[RegistroDeAcao]: ...
