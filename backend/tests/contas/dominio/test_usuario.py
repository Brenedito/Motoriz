import pytest

from motoriz.compartilhado.contexto import Papel
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import RegraViolada
from motoriz.compartilhado.ids import novo_id
from motoriz.contas.dominio.usuario import Usuario, verificar_pode_desativar


def usuario(papel: Papel = Papel.OPERADOR) -> Usuario:
    return Usuario.novo(novo_id(), "Ana", Email.de("ana@locadora.com"), papel, "hash")


def test_novo_usuario_nasce_ativo():
    assert usuario().ativo


def test_desativar_e_reativar():
    u = usuario()
    u.desativar()
    assert not u.ativo
    u.reativar()
    assert u.ativo


def test_trocar_hash_senha():
    u = usuario()
    u.trocar_hash_senha("novo")
    assert u.hash_senha == "novo"


def test_nao_pode_desativar_a_si_mesmo():
    admin = usuario(papel=Papel.ADMIN)
    with pytest.raises(RegraViolada, match="próprio usuário"):
        verificar_pode_desativar(admin, autor_id=admin.id, admins_ativos=3)


def test_nao_pode_desativar_ultimo_admin():
    alvo = usuario(papel=Papel.ADMIN)
    with pytest.raises(RegraViolada, match="ao menos um administrador"):
        verificar_pode_desativar(alvo, autor_id=novo_id(), admins_ativos=1)


def test_pode_desativar_admin_havendo_outro():
    verificar_pode_desativar(usuario(papel=Papel.ADMIN), autor_id=novo_id(), admins_ativos=2)


def test_pode_desativar_operador_mesmo_com_um_admin():
    verificar_pode_desativar(usuario(papel=Papel.OPERADOR), autor_id=novo_id(), admins_ativos=1)
