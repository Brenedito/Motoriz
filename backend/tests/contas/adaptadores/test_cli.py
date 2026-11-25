import pytest
from conftest import ContaDaApi
from fastapi.testclient import TestClient
from helpers import cnpj_valido_unico, entrar

from motoriz.compartilhado.ids import novo_id
from motoriz.contas.adaptadores.cli import main

SENHA = "senha-segura-1"


def _criar(doc: str, email: str | None = None) -> int:
    return main(
        [
            "criar-locadora",
            "--nome",
            "Loca Sul",
            "--documento",
            doc,
            "--contato",
            "x",
            "--admin-nome",
            "Ana",
            "--admin-email",
            email or f"{novo_id().hex}@x.com",
        ]
    )


def test_criar_locadora_imprime_senha(capsys: pytest.CaptureFixture[str], banco_configurado: None):
    email = f"{novo_id().hex}@x.com"
    assert _criar(cnpj_valido_unico(), email) == 0
    linhas = capsys.readouterr().out.splitlines()
    assert len(linhas) == 4
    assert linhas[0] == "Locadora criada: Loca Sul"
    assert linhas[1] == f"Admin: {email}"
    assert linhas[2].startswith("Senha inicial: ")
    assert len(linhas[2].removeprefix("Senha inicial: ")) == 16
    assert linhas[3] == "Troque a senha no primeiro acesso."


def test_documento_duplicado_sai_com_1(capsys: pytest.CaptureFixture[str], banco_configurado: None):
    doc = cnpj_valido_unico()
    assert _criar(doc) == 0
    capsys.readouterr()
    assert _criar(doc) == 1
    captura = capsys.readouterr()
    assert captura.out == ""
    assert captura.err.startswith("Erro: ")


def test_suspender_locadora_inexistente_sai_com_1(
    capsys: pytest.CaptureFixture[str], banco_configurado: None
):
    assert main(["suspender-locadora", "--documento", cnpj_valido_unico()]) == 1
    assert capsys.readouterr().err == "Erro: Locadora não encontrada\n"


def test_suspender_e_reativar(banco_configurado: None, cliente: TestClient, conta_a: ContaDaApi):
    assert main(["suspender-locadora", "--documento", conta_a.documento]) == 0
    resposta = cliente.post("/api/sessao", json={"email": conta_a.admin_email, "senha": SENHA})
    assert resposta.status_code != 204
    assert main(["reativar-locadora", "--documento", conta_a.documento]) == 0
    entrar(cliente, conta_a.admin_email, SENHA)


def test_suspender_derruba_sessao_aberta(
    banco_configurado: None, cliente: TestClient, conta_a: ContaDaApi
):
    entrar(cliente, conta_a.admin_email, SENHA)
    assert main(["suspender-locadora", "--documento", conta_a.documento]) == 0
    assert cliente.get("/api/sessao").status_code == 401


def test_sem_subcomando_e_erro_de_uso():
    with pytest.raises(SystemExit) as saida:
        main([])
    assert saida.value.code == 2
