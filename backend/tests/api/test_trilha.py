import pytest
from helpers import entrar

from motoriz.auditoria.api import MARCADOR_PESSOAL
from motoriz.compartilhado.ids import novo_id

pytestmark = pytest.mark.banco

SENHA = "senha-segura-1"


def test_trilha_do_usuario_criado(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    corpo = {
        "nome": "Bia",
        "email": f"{novo_id().hex}@locadora.com",
        "papel": "operador",
        "senha_inicial": "senha-inicial-1",
    }
    bia = cliente.post("/api/usuarios", json=corpo).json()
    cliente.post(f"/api/usuarios/{bia['id']}/desativar")
    r = cliente.get("/api/auditoria", params={"entidade": "usuario", "entidade_id": bia["id"]})
    assert r.status_code == 200
    trilha = r.json()
    assert [t["acao"] for t in trilha] == ["usuario.criado", "usuario.desativado"]
    criado = trilha[0]
    assert set(criado) == {"acao", "origem", "usuario_id", "antes", "depois", "registrado_em"}
    assert (criado["origem"], criado["usuario_id"]) == ("usuario", str(conta_a.admin_id))
    assert criado["antes"] is None
    assert criado["depois"]["nome"] == MARCADOR_PESSOAL
    assert criado["depois"]["email"] == MARCADOR_PESSOAL
    assert criado["depois"]["papel"] == "operador"
    assert criado["registrado_em"].endswith(("Z", "+00:00"))


def test_operador_tambem_consulta_trilha(cliente, conta_a):
    entrar(cliente, conta_a.operador_email, SENHA)
    r = cliente.get(
        "/api/auditoria", params={"entidade": "usuario", "entidade_id": str(conta_a.operador_id)}
    )
    assert r.status_code == 200
    assert [t["acao"] for t in r.json()] == ["usuario.criado"]


def test_trilha_sem_sessao_401(cliente):
    r = cliente.get("/api/auditoria", params={"entidade": "usuario", "entidade_id": str(novo_id())})
    assert r.status_code == 401


def test_trilha_sem_parametros_422(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    assert cliente.get("/api/auditoria").status_code == 422
