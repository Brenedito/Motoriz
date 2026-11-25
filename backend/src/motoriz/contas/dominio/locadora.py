from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID

from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.ids import novo_id


class SituacaoLocadora(StrEnum):
    ATIVA = "ativa"
    SUSPENSA = "suspensa"


@dataclass
class Locadora:
    id: UUID
    nome: str
    documento: Documento
    contato: str
    situacao: SituacaoLocadora

    @classmethod
    def nova(cls, nome: str, documento: Documento, contato: str) -> Self:
        return cls(
            id=novo_id(),
            nome=nome,
            documento=documento,
            contato=contato,
            situacao=SituacaoLocadora.ATIVA,
        )

    @property
    def ativa(self) -> bool:
        return self.situacao is SituacaoLocadora.ATIVA

    def suspender(self) -> None:
        self.situacao = SituacaoLocadora.SUSPENSA

    def reativar(self) -> None:
        self.situacao = SituacaoLocadora.ATIVA
