"""Dependências por requisição: sessão de banco, relógio e contexto da conta."""

from collections.abc import Iterator
from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker

from motoriz.compartilhado.contexto import ContextoConta
from motoriz.compartilhado.relogio import Relogio
from motoriz.contas.api import (
    RepositorioLocadorasSql,
    RepositorioSessoesSql,
    RepositorioUsuariosSql,
    ResolverSessao,
)
from motoriz.infra.conta import definir_conta, modo_plataforma

COOKIE_SESSAO = "motoriz_sessao"


def obter_sessao_banco(request: Request) -> Iterator[Session]:
    """Uma `Session` por requisição: commit no fim, rollback se a rota levantar."""
    fabrica = cast(sessionmaker[Session], request.app.state.fabrica)
    with fabrica() as sessao:
        try:
            yield sessao
        except BaseException:
            sessao.rollback()
            raise
        sessao.commit()


# `scope="function"`: o commit acontece antes de a resposta sair. Com o padrão ("request"), o
# cliente receberia 204 antes do commit, e uma falha nele não viraria resposta de erro.
SessaoBanco = Annotated[Session, Depends(obter_sessao_banco, scope="function")]


def obter_relogio(request: Request) -> Relogio:
    return cast(Relogio, request.app.state.relogio)


RelogioDaApi = Annotated[Relogio, Depends(obter_relogio)]


def obter_contexto(request: Request, sessao: SessaoBanco, relogio: RelogioDaApi) -> ContextoConta:
    """Resolve a sessão do cookie e prende a `Session` do banco à conta do usuário.

    A conta ainda não é conhecida enquanto a sessão é resolvida, por isso o modo plataforma;
    `definir_conta` o desliga em seguida. Se a sessão for inválida, `SessaoInvalida` (401) sobe
    e a `Session` é descartada sem ter servido a nenhuma conta.
    """
    modo_plataforma(sessao)
    contexto = ResolverSessao(
        locadoras=RepositorioLocadorasSql(sessao, relogio),
        usuarios=RepositorioUsuariosSql(sessao, relogio),
        sessoes=RepositorioSessoesSql(sessao),
        relogio=relogio,
    ).executar(request.cookies.get(COOKIE_SESSAO))
    definir_conta(sessao, contexto.conta_id)
    return contexto


Contexto = Annotated[ContextoConta, Depends(obter_contexto)]
