from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from testcontainers.community.mysql import MySqlContainer

from motoriz.infra.banco import criar_fabrica, criar_motor

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
