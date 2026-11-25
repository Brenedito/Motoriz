from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from helpers import entrar

from motoriz.api.dependencias import obter_relogio
from motoriz.compartilhado.relogio import RelogioFixo

pytestmark = pytest.mark.banco

SENHA = "senha-segura-1"


def test_login_com_email_em_outra_caixa_grava_cookie(cliente, conta_a):
    r = cliente.post(
        "/api/sessao", json={"email": f"  {conta_a.admin_email.upper()} ", "senha": SENHA}
    )
    assert r.status_code == 204
    cookie = r.headers["set-cookie"]
    assert "motoriz_sessao=" in cookie
    assert "httponly" in cookie.lower()
    assert "samesite=strict" in cookie.lower()
    assert f"max-age={14 * 24 * 3600}" in cookie.lower()
    assert "secure" not in cookie.lower()  # cookie_seguro=False nos testes
    assert cliente.get("/api/sessao").json()["papel"] == "admin"


def test_get_sessao_devolve_usuario_e_conta(cliente, conta_a):
    entrar(cliente, conta_a.operador_email, SENHA)
    r = cliente.get("/api/sessao")
    assert r.status_code == 200
    assert r.json() == {
        "usuario_id": str(conta_a.operador_id),
        "nome": "Operador",
        "email": conta_a.operador_email,
        "papel": "operador",
        "conta_id": str(conta_a.conta_id),
        "conta_nome": "Loca A",
    }


def test_login_errado_401_mensagem_generica(cliente, conta_a):
    r = cliente.post("/api/sessao", json={"email": conta_a.admin_email, "senha": "errada-errada"})
    assert (r.status_code, r.json()) == (401, {"erro": "E-mail ou senha incorretos."})
    assert "set-cookie" not in r.headers


def test_login_com_email_desconhecido_401_mesma_mensagem(cliente):
    r = cliente.post("/api/sessao", json={"email": "ninguem@x.com", "senha": SENHA})
    assert (r.status_code, r.json()) == (401, {"erro": "E-mail ou senha incorretos."})


def test_login_sem_campos_422_com_campos(cliente):
    r = cliente.post("/api/sessao", json={"email": "a@b.com"})
    assert r.status_code == 422
    assert r.json()["erro"] == "Dados inválidos"
    assert "senha" in r.json()["campos"]


def test_sem_cookie_401(cliente):
    r = cliente.get("/api/sessao")
    assert (r.status_code, r.json()) == (401, {"erro": "Sessão expirada. Entre novamente."})


def test_cookie_invalido_401(cliente):
    cliente.cookies.set("motoriz_sessao", "token-inventado")
    assert cliente.get("/api/sessao").status_code == 401


def test_logout_invalida_cookie(cliente, conta_a, app):
    entrar(cliente, conta_a.admin_email, SENHA)
    token = cliente.cookies.get("motoriz_sessao")
    r = cliente.delete("/api/sessao")
    assert r.status_code == 204
    assert 'motoriz_sessao=""' in r.headers["set-cookie"] or "max-age=0" in (
        r.headers["set-cookie"].lower()
    )
    assert cliente.get("/api/sessao").status_code == 401
    # O token antigo, reapresentado por outro aparelho, também não vale mais.
    outro = TestClient(app, headers={"X-Motoriz": "1"})
    outro.cookies.set("motoriz_sessao", token)
    assert outro.get("/api/sessao").status_code == 401


def test_logout_sem_sessao_204(cliente):
    assert cliente.delete("/api/sessao").status_code == 204


def test_sessao_expira_em_14_dias(cliente, conta_a, app):
    relogio = RelogioFixo(app.state.relogio.agora())
    app.dependency_overrides[obter_relogio] = lambda: relogio
    entrar(cliente, conta_a.admin_email, SENHA)
    relogio.avancar(timedelta(days=14) - timedelta(seconds=1))
    assert cliente.get("/api/sessao").status_code == 200
    relogio.avancar(timedelta(seconds=1))
    assert cliente.get("/api/sessao").status_code == 401


def test_trocar_senha_mantem_sessao_atual_e_derruba_outras(cliente, cliente_2, conta_a):
    entrar(cliente_2, conta_a.admin_email, SENHA)
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post(
        "/api/sessao/senha", json={"senha_atual": SENHA, "senha_nova": "outra-senha-forte"}
    )
    assert r.status_code == 204
    assert cliente.get("/api/sessao").status_code == 200
    assert cliente_2.get("/api/sessao").status_code == 401
    entrar(cliente_2, conta_a.admin_email, "outra-senha-forte")


def test_senha_atual_errada_422_sem_derrubar_sessao(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post(
        "/api/sessao/senha", json={"senha_atual": "errada-errada", "senha_nova": "outra-senha-1"}
    )
    assert (r.status_code, r.json()) == (422, {"erro": "Senha atual incorreta."})
    assert cliente.get("/api/sessao").status_code == 200


def test_senha_nova_longa_demais_422(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    r = cliente.post("/api/sessao/senha", json={"senha_atual": SENHA, "senha_nova": "x" * 129})
    assert r.status_code == 422
    entrar(cliente, conta_a.admin_email, SENHA)  # a senha não mudou


def test_senha_com_acentos_e_emoji_aceita(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, SENHA)
    nova = "ação-çé-🚗-segura"
    r = cliente.post("/api/sessao/senha", json={"senha_atual": SENHA, "senha_nova": nova})
    assert r.status_code == 204
    entrar(cliente, conta_a.admin_email, nova)


def test_trocar_senha_sem_sessao_401(cliente):
    r = cliente.post(
        "/api/sessao/senha", json={"senha_atual": SENHA, "senha_nova": "outra-senha-forte"}
    )
    assert r.status_code == 401
