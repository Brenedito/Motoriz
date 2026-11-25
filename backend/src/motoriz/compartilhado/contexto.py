from dataclasses import dataclass
from enum import StrEnum
from typing import Literal
from uuid import UUID

from motoriz.compartilhado.erros import AcessoNegado


class Papel(StrEnum):
    ADMIN = "admin"
    OPERADOR = "operador"


@dataclass(frozen=True)
class Ator:
    conta_id: UUID | None
    usuario_id: UUID | None
    origem: Literal["usuario", "suporte", "sistema"]


@dataclass(frozen=True)
class ContextoConta:
    conta_id: UUID
    usuario_id: UUID
    papel: Papel

    @property
    def ator(self) -> Ator:
        return Ator(conta_id=self.conta_id, usuario_id=self.usuario_id, origem="usuario")


def exigir_papel(contexto: ContextoConta, *papeis: Papel) -> None:
    if contexto.papel not in papeis:
        raise AcessoNegado("Ação não permitida para o seu perfil")
