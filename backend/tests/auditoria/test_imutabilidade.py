import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

pytestmark = pytest.mark.banco

SQLS = ["UPDATE registro_acao SET acao = 'x'", "DELETE FROM registro_acao"]


@pytest.mark.parametrize("sql", SQLS)
def test_app_nao_altera_registro(motor_app, registro_gravado, sql):
    with pytest.raises(DBAPIError), motor_app.begin() as c:
        c.execute(text(sql))


@pytest.mark.parametrize("sql", SQLS)
def test_nem_migracao_altera_registro(motor_migracao, registro_gravado, sql):
    with pytest.raises(DBAPIError, match="imutavel"), motor_migracao.begin() as c:
        c.execute(text(sql))
