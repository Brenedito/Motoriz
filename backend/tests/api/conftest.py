from collections.abc import Iterator
from dataclasses import dataclass
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from helpers import cnpj_valido_unico, entrar
from sqlalchemy import Engine

from motoriz.app import criar_app
from motoriz.auditoria.api import RegistradorSql
from motoriz.compartilhado.contexto import ContextoConta, Papel
from motoriz.compartilhado.ids import novo_id
from motoriz.contas.api import (
    CriarLocadora,
    CriarUsuario,
    RepositorioLocadorasSql,
    RepositorioUsuariosSql,
)
from motoriz.infra.banco import criar_fabrica
from motoriz.infra.config import Configuracao
from motoriz.infra.conta import modo_plataforma

__all__ = ["entrar"]  # o helper também fica à mão para quem olhar só o conftest

SENHA = "senha-segura-1"


@dataclass(frozen=True)
class ContaDaApi:
    conta_id: UUID
    documento: str
    admin_id: UUID
    admin_email: str
    operador_id: UUID
    operador_email: str


@pytest.fixture
def app(motor_app: Engine) -> Iterator[FastAPI]:
    url = motor_app.url.render_as_string(hide_password=False)
    config = Configuracao(url_banco_app=url, url_banco_migracao=url, cookie_seguro=False)
    aplicacao = criar_app(config)
    # Reaproveita o motor da sessão de testes, em vez de abrir um pool novo por teste.
    aplicacao.state.motor.dispose()
    aplicacao.state.fabrica = criar_fabrica(motor_app)
    yield aplicacao
    aplicacao.dependency_overrides.clear()


def _cliente(app: FastAPI, com_cabecalho: bool = True) -> TestClient:
    return TestClient(app, headers={"X-Motoriz": "1"} if com_cabecalho else {})


@pytest.fixture
def cliente(app: FastAPI) -> TestClient:
    return _cliente(app)


@pytest.fixture
def cliente_2(app: FastAPI) -> TestClient:
    """Outro aparelho: mesmo app, cookies separados."""
    return _cliente(app)


@pytest.fixture
def cliente_sem_cabecalho(app: FastAPI) -> TestClient:
    return _cliente(app, com_cabecalho=False)


def _criar_conta(app: FastAPI, nome: str) -> ContaDaApi:
    """Locadora com admin e operador, pelos casos de uso reais, com commit de verdade.

    Os testes de API não desfazem nada: cada conta usa documento e e-mails únicos.
    """
    hasher = app.state.hasher
    relogio = app.state.relogio
    documento = cnpj_valido_unico()
    admin_email = f"admin-{novo_id().hex}@locadora.com"
    operador_email = f"operador-{novo_id().hex}@locadora.com"
    with app.state.fabrica() as sessao:
        modo_plataforma(sessao)
        usuarios = RepositorioUsuariosSql(sessao, relogio)
        auditoria = RegistradorSql(sessao, relogio)
        criada = CriarLocadora(
            locadoras=RepositorioLocadorasSql(sessao, relogio),
            usuarios=usuarios,
            hasher=hasher,
            auditoria=auditoria,
        ).executar(nome, documento, "contato@locadora.com", "Admin", admin_email)
        # Troca a senha inicial (aleatória) por uma conhecida.
        admin = criada.admin
        admin.trocar_hash_senha(hasher.gerar(SENHA))
        usuarios.salvar(admin)
        ctx_admin = ContextoConta(
            conta_id=criada.locadora.id, usuario_id=admin.id, papel=Papel.ADMIN
        )
        operador = CriarUsuario(usuarios=usuarios, hasher=hasher, auditoria=auditoria).executar(
            ctx_admin, "Operador", operador_email, Papel.OPERADOR, SENHA
        )
        sessao.commit()
    return ContaDaApi(
        conta_id=criada.locadora.id,
        documento=documento,
        admin_id=admin.id,
        admin_email=admin_email,
        operador_id=operador.id,
        operador_email=operador_email,
    )


@pytest.fixture
def conta_a(app: FastAPI) -> ContaDaApi:
    return _criar_conta(app, "Loca A")


@pytest.fixture
def conta_b(app: FastAPI) -> ContaDaApi:
    return _criar_conta(app, "Loca B")
