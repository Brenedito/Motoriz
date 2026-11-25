from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from testcontainers.community.mysql import MySqlContainer

from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.ids import novo_id
from motoriz.contas.adaptadores.orm import LocadoraOrm, UsuarioOrm
from motoriz.contas.adaptadores.repositorios import RepositorioLocadorasSql
from motoriz.contas.dominio.locadora import Locadora
from motoriz.infra.banco import criar_fabrica, criar_motor
from motoriz.infra.conta import modo_plataforma

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
