from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from motoriz.auditoria.adaptadores.orm import RegistroAcaoOrm
from motoriz.auditoria.dominio.registro import RegistroDeAcao, mascarar
from motoriz.compartilhado.contexto import Ator
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.relogio import Relogio


def _serializavel(valor: object) -> object:
    """Converte UUID, datetime e Enum (e coleções deles) em tipos aceitos pelo JSON."""
    if isinstance(valor, Enum):
        return _serializavel(valor.value)
    if isinstance(valor, UUID):
        return str(valor)
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, Mapping):
        return {str(k): _serializavel(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple, set, frozenset)):
        return [_serializavel(v) for v in valor]
    return valor


def _preparar(
    dados: Mapping[str, object] | None, campos_pessoais: frozenset[str]
) -> dict[str, object] | None:
    mascarados = mascarar(dados, campos_pessoais)
    if mascarados is None:
        return None
    return {campo: _serializavel(valor) for campo, valor in mascarados.items()}


class RegistradorSql:
    def __init__(self, sessao: Session, relogio: Relogio) -> None:
        self._sessao = sessao
        self._relogio = relogio

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
    ) -> None:
        self._sessao.add(
            RegistroAcaoOrm(
                id=novo_id(),
                conta_id=ator.conta_id,
                usuario_id=ator.usuario_id,
                origem=ator.origem,
                acao=acao,
                entidade=entidade,
                entidade_id=entidade_id,
                antes=_preparar(antes, campos_pessoais),
                depois=_preparar(depois, campos_pessoais),
                registrado_em=self._relogio.agora(),
            )
        )

    def listar(self, conta_id: UUID, entidade: str, entidade_id: UUID) -> list[RegistroDeAcao]:
        consulta = (
            select(RegistroAcaoOrm)
            .where(
                RegistroAcaoOrm.conta_id == conta_id,
                RegistroAcaoOrm.entidade == entidade,
                RegistroAcaoOrm.entidade_id == entidade_id,
            )
            .order_by(RegistroAcaoOrm.registrado_em, RegistroAcaoOrm.id)
        )
        return [
            RegistroDeAcao(
                id=o.id,
                conta_id=o.conta_id,
                usuario_id=o.usuario_id,
                origem=o.origem,
                acao=o.acao,
                entidade=o.entidade,
                entidade_id=o.entidade_id,
                antes=o.antes,
                depois=o.depois,
                registrado_em=o.registrado_em,
            )
            for o in self._sessao.scalars(consulta)
        ]
