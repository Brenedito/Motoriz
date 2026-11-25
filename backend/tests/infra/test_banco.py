import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

pytestmark = pytest.mark.banco


def test_usuario_da_aplicacao_conecta(sessao):
    assert sessao.execute(text("SELECT 1")).scalar_one() == 1


def test_usuario_da_aplicacao_nao_cria_tabela(motor_app):
    with motor_app.connect() as conexao, pytest.raises((OperationalError, ProgrammingError)):
        conexao.execute(text("CREATE TABLE intrusa (id INT)"))
