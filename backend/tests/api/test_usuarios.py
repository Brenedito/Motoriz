import threading
import time

import pytest
from helpers import entrar

from motoriz.compartilhado.ids import novo_id
from motoriz.contas.adaptadores import repositorios

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


# --- Transições repetidas e regra do último admin sob concorrência ---------------------------


def _trilha(cliente, usuario_id) -> list[dict]:
    r = cliente.get("/api/auditoria", params={"entidade": "usuario", "entidade_id": usuario_id})
    assert r.status_code == 200
    return r.json()


def test_desativar_duas_vezes_e_idempotente_e_nao_duplica_a_trilha(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    assert cliente.post(f"/api/usuarios/{conta_a.operador_id}/desativar").status_code == 204
    antes = _trilha(cliente, str(conta_a.operador_id))
    assert cliente.post(f"/api/usuarios/{conta_a.operador_id}/desativar").status_code == 204
    depois = _trilha(cliente, str(conta_a.operador_id))
    assert depois == antes
    assert [x["acao"] for x in depois].count("usuario.desativado") == 1


def test_reativar_usuario_ativo_e_idempotente_e_nao_audita(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    antes = _trilha(cliente, str(conta_a.operador_id))
    assert cliente.post(f"/api/usuarios/{conta_a.operador_id}/reativar").status_code == 204
    assert _trilha(cliente, str(conta_a.operador_id)) == antes


def test_dois_admins_desativando_um_ao_outro_ao_mesmo_tempo(
    cliente, cliente_2, conta_a, monkeypatch
):
    entrar(cliente, conta_a.admin_email, SENHA)
    corpo = _novo_usuario("Admin2", papel="admin")
    admin2 = cliente.post("/api/usuarios", json=corpo).json()["id"]
    entrar(cliente_2, corpo["email"], corpo["senha_inicial"])

    # Alarga a janela entre contar os admins e gravar, para as duas requisições se cruzarem.
    original = repositorios.RepositorioUsuariosSql.contar_admins_ativos

    def lento(self):
        n = original(self)
        time.sleep(0.5)
        return n

    monkeypatch.setattr(repositorios.RepositorioUsuariosSql, "contar_admins_ativos", lento)
    status: dict[str, int] = {}

    def primeiro():
        status["a"] = cliente.post(f"/api/usuarios/{admin2}/desativar").status_code

    def segundo():
        status["b"] = cliente_2.post(f"/api/usuarios/{conta_a.admin_id}/desativar").status_code

    threads = [threading.Thread(target=primeiro), threading.Thread(target=segundo)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    monkeypatch.undo()

    assert sorted(status.values()) == [204, 422]
    # A conta não ficou sem administrador ativo: quem ganhou continua com acesso e admin.
    vencedor = cliente if status["a"] == 204 else cliente_2
    usuarios = vencedor.get("/api/usuarios").json()
    assert [u for u in usuarios if u["papel"] == "admin" and u["ativo"]] != []
