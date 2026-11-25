from collections.abc import Mapping
from datetime import UTC, datetime
from uuid import UUID

from motoriz.auditoria.dominio.registro import RegistroDeAcao, mascarar
from motoriz.compartilhado.contexto import Ator
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.relogio import Relogio, RelogioFixo


class RegistradorEmMemoria:
    """Implementa a porta `RegistradorDeAcoes` e o repositório de `ConsultarTrilha`."""

    def __init__(self, relogio: Relogio | None = None) -> None:
        self._relogio = relogio or RelogioFixo(datetime(2026, 11, 24, 12, 0, tzinfo=UTC))
        self.registros: list[RegistroDeAcao] = []

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
        self.registros.append(
            RegistroDeAcao(
                id=novo_id(),
                conta_id=ator.conta_id,
                usuario_id=ator.usuario_id,
                origem=ator.origem,
                acao=acao,
                entidade=entidade,
                entidade_id=entidade_id,
                antes=mascarar(antes, campos_pessoais),
                depois=mascarar(depois, campos_pessoais),
                registrado_em=self._relogio.agora(),
            )
        )

    def listar(self, conta_id: UUID, entidade: str, entidade_id: UUID) -> list[RegistroDeAcao]:
        return sorted(
            (
                r
                for r in self.registros
                if r.conta_id == conta_id
                and r.entidade == entidade
                and r.entidade_id == entidade_id
            ),
            key=lambda r: r.registrado_em,
        )
