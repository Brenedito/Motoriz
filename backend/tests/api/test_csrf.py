"""O middleware recusa antes de qualquer rota rodar; só o primeiro teste usa o banco (fixture)."""

from fastapi.testclient import TestClient

from motoriz.app import criar_app


def test_post_sem_cabecalho_403(cliente_sem_cabecalho):
    r = cliente_sem_cabecalho.post("/api/sessao", json={"email": "a@b.com", "senha": "x" * 10})
    assert (r.status_code, r.json()) == (403, {"erro": "Requisição não permitida"})


def test_cabecalho_com_outro_valor_403():
    cliente = TestClient(criar_app(), headers={"X-Motoriz": "0"})
    assert cliente.delete("/api/sessao").status_code == 403


def test_metodos_que_alteram_exigem_cabecalho():
    cliente = TestClient(criar_app())
    for metodo in ("POST", "PUT", "PATCH", "DELETE"):
        assert cliente.request(metodo, "/api/usuarios").status_code == 403, metodo


def test_get_sem_cabecalho_passa():
    assert TestClient(criar_app()).get("/api/saude").status_code == 200
