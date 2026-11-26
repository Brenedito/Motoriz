from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID

from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.texto import texto_obrigatorio

TAMANHO_MAXIMO_NOME = 200  # coluna `locadora.nome`
TAMANHO_MAXIMO_CONTATO = 200  # coluna `locadora.contato`


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
            nome=texto_obrigatorio(nome, campo="nome", maximo=TAMANHO_MAXIMO_NOME),
            documento=documento,
            contato=texto_obrigatorio(contato, campo="contato", maximo=TAMANHO_MAXIMO_CONTATO),
            situacao=SituacaoLocadora.ATIVA,
        )

    @property
    def ativa(self) -> bool:
        return self.situacao is SituacaoLocadora.ATIVA

    def suspender(self) -> None:
        self.situacao = SituacaoLocadora.SUSPENSA

    def reativar(self) -> None:
        self.situacao = SituacaoLocadora.ATIVA
