import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, text

from motoriz.infra.banco import Base
from motoriz.infra.config import obter_configuracao

# Permite que as migrações importem `conceder` (alembic/conceder.py).
sys.path.insert(0, str(Path(__file__).parent))

# As Tasks 5 e 6 importam aqui os mapeamentos ORM para popular Base.metadata:
#   motoriz.contas.adaptadores.orm
#   motoriz.auditoria.adaptadores.orm

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _url() -> str:
    return config.get_main_option("sqlalchemy.url") or obter_configuracao().url_banco_migracao


def run_migrations_offline() -> None:
    context.configure(
        url=_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    motor = create_engine(_url())
    with motor.connect() as conexao:
        context.configure(connection=conexao, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        # O MySQL só deixa `motoriz_app` abrir o schema se ele tiver algum privilégio nele;
        # a leitura de alembic_version garante isso mesmo antes da primeira tabela de negócio.
        conexao.execute(text("GRANT SELECT ON alembic_version TO 'motoriz_app'@'%'"))
    motor.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
