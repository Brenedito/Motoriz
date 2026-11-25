from datetime import UTC, datetime

import pytest
from conftest import locadora_orm, usuario_orm
from sqlalchemy import delete, exists, func, insert, select, text, update
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import ObjectDeletedError

from motoriz.compartilhado.ids import novo_id
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
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    stmt = select(UsuarioOrm).execution_options(todas_as_contas=True)
    assert {a.email, b.email} <= {u.email for u in sessao.scalars(stmt)}


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
    definir_conta(sessao, a.conta_id)
    usuario_b = sessao.scalars(
        select(UsuarioOrm)
        .where(UsuarioOrm.id == b.usuario_id)
        .execution_options(todas_as_contas=True)
    ).one()
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
    a, b = duas_contas
    modo_plataforma(sessao)
    assert {a.email, b.email} <= {u.email for u in sessao.scalars(select(UsuarioOrm))}


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
        email: nome
        for email, nome in sessao.execute(
            select(UsuarioOrm.email, UsuarioOrm.nome).where(
                UsuarioOrm.conta_id.in_([a.conta_id, b.conta_id])
            )
        )
    }
    assert nomes == {a.email: "Alterado", b.email: "Ana"}


def test_update_em_massa_sem_conta_falha(sessao, duas_contas):
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(update(UsuarioOrm).values(nome="Alterado"))


def test_tabela_fora_da_conta_nao_exige_conta(sessao, duas_contas):
    ids = {c.conta_id for c in duas_contas}
    assert ids <= {loc.id for loc in sessao.scalars(select(LocadoraOrm))}


def test_sql_textual_passa_direto(sessao, duas_contas):
    assert _total_de_usuarios(sessao, duas_contas) == 2


def test_locadora_nao_e_da_conta(sessao):
    sessao.add(locadora_orm("52998224725"))
    sessao.flush()


# --- Regressões da revisão: Core sobre Table, insert() e tomada de linha de outra conta -------

TABELA = UsuarioOrm.__table__


def _valores_insert(conta_id):
    return {
        "id": novo_id(),
        "conta_id": conta_id,
        "nome": "Intrusa",
        "email": f"{novo_id().hex}@x.com",
        "papel": "operador",
        "hash_senha": "h",
        "ativo": True,
        "versao": 1,
        "criado_em": datetime.now(UTC),
    }


def _total_de_usuarios(sessao, contas):
    # Só das contas do teste: os testes de API gravam (com commit) outras contas no mesmo banco.
    a, b = contas
    sql = text("SELECT COUNT(*) FROM usuario WHERE conta_id IN (:a, :b)")
    return sessao.execute(sql, {"a": a.conta_id.bytes, "b": b.conta_id.bytes}).scalar_one()


def test_core_select_em_tabela_da_conta_e_recusado(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(select(TABELA.c.email)).all()


def test_core_select_misturado_com_orm_e_recusado(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(select(UsuarioOrm.email).where(TABELA.c.nome == "Ana")).all()


def test_core_update_em_tabela_da_conta_e_recusado(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(update(TABELA).values(nome="X"))
    assert sessao.execute(text("SELECT COUNT(*) FROM usuario WHERE nome = 'X'")).scalar() == 0


def test_core_delete_em_tabela_da_conta_e_recusado(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(delete(TABELA))


def test_core_insert_em_tabela_da_conta_e_recusado(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(insert(TABELA).values(**_valores_insert(b.conta_id)))
    assert _total_de_usuarios(sessao, duas_contas) == 2


def test_orm_insert_em_tabela_da_conta_e_recusado(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(insert(UsuarioOrm).values(**_valores_insert(b.conta_id)))
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(insert(UsuarioOrm), [_valores_insert(a.conta_id)])
    assert _total_de_usuarios(sessao, duas_contas) == 2


def test_core_e_insert_liberados_em_modo_plataforma(sessao, duas_contas):
    a, b = duas_contas
    modo_plataforma(sessao)
    contas = [a.conta_id, b.conta_id]
    emails = set(sessao.execute(select(TABELA.c.email)).scalars())
    assert {a.email, b.email} <= emails
    alterar = update(TABELA).where(TABELA.c.conta_id.in_(contas)).values(nome="X")
    assert sessao.execute(alterar).rowcount == 2
    sessao.execute(insert(TABELA).values(**_valores_insert(b.conta_id)))
    sessao.execute(insert(UsuarioOrm).values(**_valores_insert(a.conta_id)))
    assert _total_de_usuarios(sessao, duas_contas) == 4


def test_core_liberado_com_todas_as_contas(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    stmt = select(TABELA.c.email).execution_options(todas_as_contas=True)
    assert {a.email, b.email} <= set(sessao.execute(stmt).scalars())


def test_tomar_usuario_de_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    usuario_b = sessao.scalars(
        select(UsuarioOrm)
        .where(UsuarioOrm.id == b.usuario_id)
        .execution_options(todas_as_contas=True)
    ).one()
    usuario_b.conta_id = a.conta_id
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_apagar_usuario_de_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    usuario_b = sessao.scalars(
        select(UsuarioOrm)
        .where(UsuarioOrm.id == b.usuario_id)
        .execution_options(todas_as_contas=True)
    ).one()
    sessao.delete(usuario_b)
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_plataforma_pode_mover_usuario_de_conta(sessao, duas_contas):
    a, b = duas_contas
    modo_plataforma(sessao)
    usuario_b = sessao.get(UsuarioOrm, b.usuario_id)
    usuario_b.conta_id = a.conta_id
    sessao.flush()


def test_core_escondido_em_alias_de_outra_entidade_e_recusado(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    sub = select(TABELA.c.conta_id.label("id")).subquery()
    falsa = aliased(LocadoraOrm, sub, adapt_on_names=True)
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(select(falsa.id)).all()


# --- Regressões da 2ª revisão: cargas por identidade, exists() e conta_id não carregado ------


def _usuario_de_b(sessao, b):
    stmt = (
        select(UsuarioOrm)
        .where(UsuarioOrm.id == b.usuario_id)
        .execution_options(todas_as_contas=True)
    )
    return sessao.scalars(stmt).one()


def test_get_da_propria_conta_e_de_outra(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    assert sessao.get(UsuarioOrm, a.usuario_id) is not None
    assert sessao.get(UsuarioOrm, b.usuario_id) is None


def test_get_sem_conta_falha(sessao, duas_contas):
    sessao.expunge_all()
    with pytest.raises(ContextoDeContaAusente):
        sessao.get(UsuarioOrm, duas_contas[0].usuario_id)


def test_definir_conta_tira_objetos_de_outra_conta_do_mapa(sessao, duas_contas):
    a, b = duas_contas
    modo_plataforma(sessao)
    sessao.get(UsuarioOrm, b.usuario_id)
    definir_conta(sessao, a.conta_id)
    assert sessao.get(UsuarioOrm, b.usuario_id) is None


def test_definir_conta_com_alteracao_pendente_de_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    modo_plataforma(sessao)
    sessao.get(UsuarioOrm, b.usuario_id).nome = "Pendente"
    with pytest.raises(ContextoDeContaAusente):
        definir_conta(sessao, a.conta_id)


def test_atributo_expirado_recarrega(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    u = sessao.scalars(select(UsuarioOrm)).one()
    sessao.expire(u)
    assert u.email == a.email


def test_recarga_troca_de_conta_nao_reaproveita_o_filtro(sessao, duas_contas):
    a, b = duas_contas
    for conta in (a, b, a):
        definir_conta(sessao, conta.conta_id)
        u = sessao.scalars(select(UsuarioOrm)).one()
        sessao.expire(u)
        assert u.email == conta.email


def test_refresh(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    u = sessao.scalars(select(UsuarioOrm)).one()
    sessao.refresh(u)
    assert u.email == a.email


def test_atributo_depois_do_commit(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    u = sessao.scalars(select(UsuarioOrm)).one()
    sessao.commit()
    assert u.email == a.email


def test_atributo_depois_do_commit_redefinindo_a_mesma_conta(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    u = sessao.scalars(select(UsuarioOrm)).one()
    sessao.commit()
    definir_conta(sessao, a.conta_id)
    assert u.email == a.email


def test_trocar_de_conta_tira_objetos_expirados_do_mapa(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    u = sessao.scalars(select(UsuarioOrm)).one()
    sessao.commit()
    definir_conta(sessao, b.conta_id)
    assert u not in sessao
    assert sessao.get(UsuarioOrm, a.usuario_id) is None


def test_recarga_de_objeto_de_outra_conta_nao_devolve_a_linha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    usuario_b = _usuario_de_b(sessao, b)
    sessao.expire(usuario_b)
    with pytest.raises(ObjectDeletedError):
        _ = usuario_b.email


def test_exists_orm_funciona_e_e_filtrado(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    assert sessao.scalar(select(exists().where(UsuarioOrm.email == a.email))) is True
    assert sessao.scalar(select(exists().where(UsuarioOrm.email == b.email))) is False


def test_exists_orm_sem_conta_falha(sessao, duas_contas):
    with pytest.raises(ContextoDeContaAusente):
        sessao.scalar(select(exists().where(UsuarioOrm.email == duas_contas[0].email)))


def test_exists_core_e_recusado(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    stmt = select(LocadoraOrm.nome).where(exists().where(TABELA.c.conta_id == LocadoraOrm.id))
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(stmt).all()


def test_tomar_usuario_com_conta_id_expirado_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    usuario_b = _usuario_de_b(sessao, b)
    sessao.expire(usuario_b, ["conta_id"])
    usuario_b.conta_id = a.conta_id
    usuario_b.nome = "hack"
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_tomar_usuario_totalmente_expirado_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    usuario_b = _usuario_de_b(sessao, b)
    sessao.commit()
    usuario_b.conta_id = a.conta_id
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()


def test_alterar_objeto_proprio_expirado_passa(sessao, duas_contas):
    a, _ = duas_contas
    definir_conta(sessao, a.conta_id)
    u = sessao.scalars(select(UsuarioOrm)).one()
    sessao.commit()
    u.nome = "Novo"
    sessao.flush()
    assert sessao.scalars(select(UsuarioOrm.nome)).one() == "Novo"
