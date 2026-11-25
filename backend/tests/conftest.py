from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from helpers import cnpj_valido_unico, entrar
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session
from testcontainers.community.mysql import MySqlContainer

from motoriz.app import criar_app
from motoriz.auditoria.api import RegistradorSql
from motoriz.compartilhado.contexto import ContextoConta, Papel
from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.relogio import RelogioFixo
from motoriz.contas.adaptadores.orm import LocadoraOrm, UsuarioOrm
from motoriz.contas.adaptadores.repositorios import (
    RepositorioLocadorasSql,
    RepositorioUsuariosSql,
)
from motoriz.contas.api import CriarLocadora, CriarUsuario
from motoriz.contas.dominio.locadora import Locadora
from motoriz.infra.banco import criar_fabrica, criar_motor
from motoriz.infra.config import Configuracao, obter_configuracao
from motoriz.infra.conta import modo_plataforma

__all__ = ["entrar"]  # o helper também fica à mão para quem olhar só o conftest

RAIZ = Path(__file__).resolve().parents[2]
ALEMBIC_INI = RAIZ / "backend" / "alembic.ini"
INIT_SQL = RAIZ / "infra" / "mysql" / "init.sql"
COMANDO_MYSQL = (
    "--log-bin-trust-function-creators=1 "
    "--character-set-server=utf8mb4 --collation-server=utf8mb4_0900_ai_ci"
)


@pytest.fixture(scope="session")
def mysql_container() -> Iterator[MySqlContainer]:
    container = (
        MySqlContainer("mysql:8.4", dbname="motoriz")
        .with_volume_mapping(str(INIT_SQL), "/docker-entrypoint-initdb.d/init.sql")
        .with_command(COMANDO_MYSQL)
    )
    with container:
        yield container


def _url(container: MySqlContainer, usuario: str, senha: str) -> str:
    host = container.get_container_host_ip()
    porta = container.get_exposed_port(3306)
    return f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/motoriz"


@pytest.fixture(scope="session")
def motor_migracao(mysql_container: MySqlContainer) -> Iterator[Engine]:
    url = _url(mysql_container, "motoriz_migracao", "migracao_dev")
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")
    motor = criar_motor(url)
    yield motor
    motor.dispose()


@pytest.fixture(scope="session")
def motor_app(mysql_container: MySqlContainer, motor_migracao: Engine) -> Iterator[Engine]:
    motor = criar_motor(_url(mysql_container, "motoriz_app", "app_dev"))
    yield motor
    motor.dispose()


@pytest.fixture
def sessao(motor_app: Engine) -> Iterator[Session]:
    fabrica = criar_fabrica(motor_app)
    with motor_app.connect() as conexao:
        externa = conexao.begin()
        with fabrica(bind=conexao, join_transaction_mode="create_savepoint") as s:
            yield s
        externa.rollback()


# --- Contas -----------------------------------------------------------------------------------
# Estas fixtures ficam aqui, e não em tests/contas/conftest.py, porque o teste do filtro de conta
# (tests/infra) também usa: o pytest só enxerga conftest.py de diretórios ancestrais.


@dataclass(frozen=True)
class ContaDeTeste:
    conta_id: UUID
    usuario_id: UUID
    email: str


def locadora_orm(documento: str, nome: str = "Locadora") -> LocadoraOrm:
    return LocadoraOrm(
        id=novo_id(),
        nome=nome,
        documento=documento,
        tipo_documento="CNPJ" if len(documento) == 14 else "CPF",
        contato="contato@locadora.com",
        situacao="ativa",
        criada_em=datetime.now(UTC),
    )


def usuario_orm(conta_id: UUID, email: str | None = None, nome: str = "Ana") -> UsuarioOrm:
    return UsuarioOrm(
        id=novo_id(),
        conta_id=conta_id,
        nome=nome,
        email=email or f"{novo_id().hex}@locadora.com",
        papel="operador",
        hash_senha="hash",
        ativo=True,
        versao=1,
        criado_em=datetime.now(UTC),
    )


@pytest.fixture
def duas_contas(sessao: Session) -> tuple[ContaDeTeste, ContaDeTeste]:
    """Duas locadoras com um usuário cada, gravadas em modo plataforma."""
    modo_plataforma(sessao)
    contas = []
    for documento, email in (("11222333000181", "a@a.com"), ("11444777000161", "b@b.com")):
        loc = locadora_orm(documento)
        sessao.add(loc)
        sessao.flush()
        usu = usuario_orm(loc.id, email)
        sessao.add(usu)
        sessao.flush()
        contas.append(ContaDeTeste(conta_id=loc.id, usuario_id=usu.id, email=email))
    sessao.info.clear()
    return contas[0], contas[1]


@pytest.fixture
def locadora_gravada(sessao: Session) -> Locadora:
    modo_plataforma(sessao)
    loc = Locadora.nova("Locadora X", Documento.de("11222333000181"), "x@locadora.com")
    RepositorioLocadorasSql(sessao).adicionar(loc)
    sessao.info.clear()
    return loc


# --- Auditoria --------------------------------------------------------------------------------


@pytest.fixture
def relogio_fixo() -> RelogioFixo:
    return RelogioFixo(datetime(2026, 11, 24, 12, 0, tzinfo=UTC))


@pytest.fixture
def registro_gravado(motor_migracao: Engine) -> UUID:
    """Grava um registro com id único e não limpa depois: a tabela é imutável por definição."""
    id_ = novo_id()
    with motor_migracao.begin() as conexao:
        conexao.execute(
            text(
                "INSERT INTO registro_acao (id, conta_id, usuario_id, origem, acao, entidade, "
                "entidade_id, antes, depois, registrado_em) "
                "VALUES (:id, NULL, NULL, 'sistema', 'teste.gravado', 'teste', :alvo, "
                "NULL, NULL, '2026-11-24 12:00:00.000000')"
            ),
            {"id": id_.bytes, "alvo": novo_id().bytes},
        )
    return id_


# --- API --------------------------------------------------------------------------------------
# Aqui (e não em tests/api) porque tests/contas/adaptadores e tests/isolamento também usam.


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


@pytest.fixture
def banco_configurado(
    monkeypatch: pytest.MonkeyPatch, motor_app: Engine, motor_migracao: Engine
) -> Iterator[None]:
    """Aponta a configuração (lida do ambiente) para o MySQL do teste."""
    url_app = motor_app.url.render_as_string(hide_password=False)
    url_migracao = motor_migracao.url.render_as_string(hide_password=False)
    monkeypatch.setenv("MOTORIZ_URL_BANCO_APP", url_app)
    monkeypatch.setenv("MOTORIZ_URL_BANCO_MIGRACAO", url_migracao)
    obter_configuracao.cache_clear()
    yield
    obter_configuracao.cache_clear()
