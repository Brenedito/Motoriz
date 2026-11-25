from fastapi.testclient import TestClient

from motoriz.app import criar_app


def test_saude_responde_ok() -> None:
    resposta = TestClient(criar_app()).get("/api/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
