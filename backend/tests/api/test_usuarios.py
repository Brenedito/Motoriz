import pytest
from helpers import entrar

from motoriz.compartilhado.ids import novo_id

pytestmark = pytest.mark.banco

SENHA = "senha-segura-1"


def _novo_usuario(nome: str = "Bia", papel: str = "operador") -> dict[str, str]:
    return {
        "nome": nome,
        "email": f"{novo_id().hex}@locadora.com",
        "papel": papel,
        "senha_inicial": "senha-inicial-1",
    }


def test_admin_cria_e_lista(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    corpo = _novo_usuario()
    r = cliente.post("/api/usuarios", json={**corpo, "email": f"  {corpo['email'].upper()} "})
    assert r.status_code == 201
    criado = r.json()
    assert criado == {
        "id": criado["id"],
        "nome": "Bia",
        "email": corpo["email"],
        "papel": "operador",
        "ativo": True,
    }
    lista = cliente.get("/api/usuarios")
    assert lista.status_code == 200
    assert [u["nome"] for u in lista.json()] == ["Admin", "Bia", "Operador"]
    assert criado in lista.json()


def test_usuario_criado_consegue_entrar(cliente, cliente_2, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    corpo = _novo_usuario()
    assert cliente.post("/api/usuarios", json=corpo).status_code == 201
    entrar(cliente_2, corpo["email"], corpo["senha_inicial"])
    assert cliente_2.get("/api/sessao").json()["conta_id"] == str(conta_a.conta_id)


def test_operador_recebe_403(cliente, conta_a):
    entrar(cliente, conta_a.operador_email, SENHA)
    r = cliente.get("/api/usuarios")
    assert (r.status_code, r.json()) == (403, {"erro": "Ação não permitida para o seu perfil"})
    assert cliente.post("/api/usuarios", json=_novo_usuario()).status_code == 403


def test_sem_sessao_401(cliente):
    assert cliente.get("/api/usuarios").status_code == 401


def test_admin_nao_desativa_a_si_mesmo(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post(f"/api/usuarios/{conta_a.admin_id}/desativar")
    assert (r.status_code, r.json()["erro"]) == (
        422,
        "Você não pode desativar o seu próprio usuário",
    )


def test_usuario_desativado_perde_sessao_aberta(cliente, cliente_2, conta_a):
    entrar(cliente_2, conta_a.operador_email, SENHA)
    entrar(cliente, conta_a.admin_email, SENHA)
    assert cliente.post(f"/api/usuarios/{conta_a.operador_id}/desativar").status_code == 204
    assert cliente_2.get("/api/sessao").status_code == 401
    r = cliente_2.post("/api/sessao", json={"email": conta_a.operador_email, "senha": SENHA})
    assert r.status_code == 401


def test_reativar_devolve_acesso(cliente, cliente_2, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    assert cliente.post(f"/api/usuarios/{conta_a.operador_id}/desativar").status_code == 204
    assert cliente.post(f"/api/usuarios/{conta_a.operador_id}/reativar").status_code == 204
    entrar(cliente_2, conta_a.operador_email, SENHA)
    usuarios = {u["id"]: u for u in cliente.get("/api/usuarios").json()}
    assert usuarios[str(conta_a.operador_id)]["ativo"] is True


def test_desativar_inexistente_404(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post(f"/api/usuarios/{novo_id()}/desativar")
    assert (r.status_code, r.json()) == (404, {"erro": "Usuário não encontrado"})


def test_id_malformado_422(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post("/api/usuarios/nao-e-uuid/desativar")
    assert (r.status_code, r.json()["erro"]) == (422, "Dados inválidos")


def test_email_duplicado_409(cliente, conta_a, conta_b):
    entrar(cliente, conta_a.admin_email, SENHA)
    # O e-mail é único na plataforma: o de um admin de outra locadora também conflita.
    corpo = {**_novo_usuario(), "email": conta_b.admin_email.upper()}
    r = cliente.post("/api/usuarios", json=corpo)
    assert (r.status_code, r.json()) == (409, {"erro": "Já existe um usuário com este e-mail"})


def test_senha_inicial_fraca_422(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post("/api/usuarios", json={**_novo_usuario(), "senha_inicial": "curta"})
    assert r.status_code == 422
    assert "senha" in r.json()["erro"].lower()


def test_papel_invalido_422(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post("/api/usuarios", json={**_novo_usuario(), "papel": "dono"})
    assert (r.status_code, r.json()["erro"]) == (422, "Dados inválidos")
    assert "papel" in r.json()["campos"]
