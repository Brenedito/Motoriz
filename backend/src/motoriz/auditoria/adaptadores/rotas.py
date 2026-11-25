"""Rota HTTP da trilha de auditoria."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from motoriz.api.dependencias import Contexto, RelogioDaApi, SessaoBanco
from motoriz.auditoria.adaptadores.registrador_sql import RegistradorSql
from motoriz.auditoria.aplicacao.consultar import ConsultarTrilha

roteador = APIRouter(prefix="/api")


class RegistroSaida(BaseModel):
    acao: str
    origem: str
    usuario_id: UUID | None
    antes: dict[str, object] | None
    depois: dict[str, object] | None
    registrado_em: datetime


@roteador.get("/auditoria", tags=["auditoria"])
def consultar_trilha(
    entidade: str,
    entidade_id: UUID,
    contexto: Contexto,
    sessao: SessaoBanco,
    relogio: RelogioDaApi,
) -> list[RegistroSaida]:
    registros = ConsultarTrilha(RegistradorSql(sessao, relogio)).executar(
        contexto, entidade, entidade_id
    )
    return [
        RegistroSaida(
            acao=r.acao,
            origem=r.origem,
            usuario_id=r.usuario_id,
            antes=r.antes,
            depois=r.depois,
            registrado_em=r.registrado_em,
        )
        for r in registros
    ]
