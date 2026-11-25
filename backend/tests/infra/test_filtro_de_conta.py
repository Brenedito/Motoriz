import pytest
from conftest import locadora_orm, usuario_orm
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import aliased

from motoriz.contas.adaptadores.orm import LocadoraOrm, UsuarioOrm
from motoriz.infra.banco import criar_fabrica
from motoriz.infra.conta import ContextoDeContaAusente, definir_conta, modo_plataforma

pytestmark = pytest.mark.banco


def test_consulta_sem_conta_falha(sessao):
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(select(UsuarioOrm)).all()


def test_consulta_so_ve_a_propria_conta(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    emails = [u.email for u in sessao.scalars(select(UsuarioOrm))]
    assert emails == [a.email]


def test_gravar_objeto_de_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    sessao.add(usuario_orm(conta_id=b.conta_id))
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_todas_as_contas_e_explicito(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    stmt = select(UsuarioOrm).execution_options(todas_as_contas=True)
    assert len(sessao.scalars(stmt).all()) == 2


def test_gravar_sem_conta_falha(sessao, duas_contas):
    sessao.add(usuario_orm(conta_id=duas_contas[0].conta_id))
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_gravar_na_propria_conta_passa(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    sessao.add(usuario_orm(conta_id=a.conta_id))
    sessao.flush()
    assert len(sessao.scalars(select(UsuarioOrm)).all()) == 2


def test_alterar_objeto_de_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    modo_plataforma(sessao)
    usuario_b = sessao.get(UsuarioOrm, b.usuario_id)
    sessao.info.clear()
    definir_conta(sessao, a.conta_id)
    usuario_b.nome = "Invasor"
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_mover_objeto_para_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    usuario_a = sessao.scalars(select(UsuarioOrm)).one()
    usuario_a.conta_id = b.conta_id
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_modo_plataforma_ve_todas(sessao, duas_contas):
    modo_plataforma(sessao)
    assert len(sessao.scalars(select(UsuarioOrm)).all()) == 2


def test_definir_conta_sai_do_modo_plataforma(sessao, duas_contas):
    a, _ = duas_contas
    modo_plataforma(sessao)
    definir_conta(sessao, a.conta_id)
    assert [u.email for u in sessao.scalars(select(UsuarioOrm))] == [a.email]


def test_trocar_de_conta_na_mesma_sessao_nao_reaproveita_o_filtro(sessao, duas_contas):
    """O lambda do critério vira parâmetro: o cache de SQL não pode fixar a primeira conta."""
    a, b = duas_contas
    stmt = select(UsuarioOrm.email)
    definir_conta(sessao, a.conta_id)
    assert sessao.scalars(stmt).all() == [a.email]
    definir_conta(sessao, b.conta_id)
    assert sessao.scalars(stmt).all() == [b.email]
    definir_conta(sessao, a.conta_id)
    assert sessao.scalars(select(UsuarioOrm.email)).all() == [a.email]


def test_outra_sessao_do_mesmo_motor_usa_a_propria_conta(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    assert sessao.scalars(select(UsuarioOrm.email)).all() == [a.email]
    conexao = sessao.connection()
    fabrica = criar_fabrica(conexao.engine)
    with fabrica(bind=conexao, join_transaction_mode="create_savepoint") as outra:
        definir_conta(outra, b.conta_id)
        assert outra.scalars(select(UsuarioOrm.email)).all() == [b.email]


def test_contagem_por_select_from_e_filtrada(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    total = sessao.scalar(select(func.count()).select_from(UsuarioOrm))
    assert total == 1


def test_contagem_por_select_from_sem_conta_falha(sessao, duas_contas):
    with pytest.raises(ContextoDeContaAusente):
        sessao.scalar(select(func.count()).select_from(UsuarioOrm))


def test_join_a_partir_de_tabela_fora_da_conta_e_filtrado(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    stmt = select(LocadoraOrm.id).join(UsuarioOrm, UsuarioOrm.conta_id == LocadoraOrm.id)
    assert sessao.scalars(stmt).all() == [a.conta_id]


def test_subconsulta_e_filtrada(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    sub = select(UsuarioOrm.conta_id).scalar_subquery()
    stmt = select(LocadoraOrm.id).where(LocadoraOrm.id.in_(sub))
    assert sessao.scalars(stmt).all() == [a.conta_id]


def test_alias_e_filtrado(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    u = aliased(UsuarioOrm)
    assert [x.email for x in sessao.scalars(select(u))] == [a.email]


def test_update_em_massa_so_afeta_a_propria_conta(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    sessao.execute(update(UsuarioOrm).values(nome="Alterado"))
    modo_plataforma(sessao)
    nomes = {
        email: nome for email, nome in sessao.execute(select(UsuarioOrm.email, UsuarioOrm.nome))
    }
    assert nomes == {a.email: "Alterado", b.email: "Ana"}


def test_update_em_massa_sem_conta_falha(sessao, duas_contas):
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(update(UsuarioOrm).values(nome="Alterado"))


def test_tabela_fora_da_conta_nao_exige_conta(sessao, duas_contas):
    assert len(sessao.scalars(select(LocadoraOrm)).all()) == 2


def test_sql_textual_passa_direto(sessao, duas_contas):
    assert sessao.execute(text("SELECT COUNT(*) FROM usuario")).scalar_one() == 2


def test_locadora_nao_e_da_conta(sessao):
    sessao.add(locadora_orm("52998224725"))
    sessao.flush()
