from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

MARCADOR_PESSOAL = "[dado pessoal]"


@dataclass(frozen=True)
class RegistroDeAcao:
    id: UUID
    conta_id: UUID | None
    usuario_id: UUID | None
    origem: str
    acao: str
    entidade: str
    entidade_id: UUID
    antes: dict[str, object] | None
    depois: dict[str, object] | None
    registrado_em: datetime


def mascarar(
    dados: Mapping[str, object] | None, campos_pessoais: frozenset[str]
) -> dict[str, object] | None:
    """Troca o valor de cada campo pessoal presente por `MARCADOR_PESSOAL`, sem alterar `dados`."""
    if dados is None:
        return None
    return {
        campo: MARCADOR_PESSOAL if campo in campos_pessoais else valor
        for campo, valor in dados.items()
    }
