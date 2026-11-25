import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from motoriz.infra.banco import Base

pytestmark = pytest.mark.banco


def test_migracao_bate_com_o_orm(motor_migracao):
    with motor_migracao.connect() as conexao:
        diferencas = compare_metadata(MigrationContext.configure(conexao), Base.metadata)
    assert diferencas == []


@pytest.mark.parametrize("tabela", ["locadora", "usuario", "sessao"])
def test_app_nao_apaga_dado_de_contas(motor_app, tabela):
    with motor_app.connect() as conexao, pytest.raises((OperationalError, ProgrammingError)):
        conexao.execute(text(f"DELETE FROM {tabela}"))
