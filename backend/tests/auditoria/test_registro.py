from motoriz.auditoria.dominio.registro import MARCADOR_PESSOAL, mascarar


def test_mascarar_troca_so_campos_pessoais():
    dados = {"nome": "Ana", "email": "ana@x.com", "papel": "admin"}
    assert mascarar(dados, frozenset({"nome", "email"})) == {
        "nome": MARCADOR_PESSOAL,
        "email": MARCADOR_PESSOAL,
        "papel": "admin",
    }
    assert dados["nome"] == "Ana"


def test_mascarar_none():
    assert mascarar(None, frozenset({"nome"})) is None


def test_mascarar_ignora_campo_pessoal_ausente():
    assert mascarar({"papel": "admin"}, frozenset({"nome"})) == {"papel": "admin"}
