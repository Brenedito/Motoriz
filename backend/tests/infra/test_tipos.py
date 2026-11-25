import pytest
from sqlalchemy import Engine, bindparam, text

from motoriz.compartilhado.ids import novo_id
from motoriz.infra.tipos import UUIDBinario

pytestmark = pytest.mark.banco


def test_uuid_binario_ida_e_volta(motor_migracao: Engine) -> None:
    valor = novo_id()
    insercao = text("INSERT INTO t (id) VALUES (:id)").bindparams(
        bindparam("id", type_=UUIDBinario())
    )
    consulta = text("SELECT id FROM t").columns(id=UUIDBinario())
    with motor_migracao.connect() as conexao:
        conexao.execute(text("CREATE TEMPORARY TABLE t (id BINARY(16))"))
        conexao.execute(insercao, {"id": valor})
        bruto = conexao.execute(text("SELECT id FROM t")).scalar_one()
        lido = conexao.execute(consulta).scalar_one()
    assert bruto == valor.bytes
    assert lido == valor
