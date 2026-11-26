import pytest

from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.texto import TextoInvalido
from motoriz.contas.dominio.erros import (
    CredenciaisInvalidas,
    EmailJaCadastrado,
    LocadoraJaCadastrada,
    SessaoInvalida,
)
from motoriz.contas.dominio.locadora import Locadora, SituacaoLocadora


def test_locadora_suspensa_e_reativada():
    loc = Locadora.nova("Loca Sul", Documento.de("11.222.333/0001-81"), "(51) 99999-0000")
    assert loc.ativa
    loc.suspender()
    assert not loc.ativa
    assert loc.situacao is SituacaoLocadora.SUSPENSA
    loc.reativar()
    assert loc.ativa


def test_mensagens_padrao_dos_erros():
    assert CredenciaisInvalidas().mensagem == "E-mail ou senha incorretos."
    assert SessaoInvalida().mensagem == "Sessão expirada. Entre novamente."
    assert EmailJaCadastrado().mensagem == "Já existe um usuário com este e-mail"
    assert LocadoraJaCadastrada().mensagem == "Já existe uma locadora com este documento"
    assert EmailJaCadastrado("outra").mensagem == "outra"


def test_nome_e_contato_da_locadora_sao_aparados():
    loc = Locadora.nova("  Loca Sul ", Documento.de("11.222.333/0001-81"), " (51) 9999 ")
    assert (loc.nome, loc.contato) == ("Loca Sul", "(51) 9999")


@pytest.mark.parametrize(
    ("nome", "contato", "mensagem"),
    [
        ("  ", "(51) 9999", "Informe o nome"),
        ("Loca Sul", "", "Informe o contato"),
        ("a" * 201, "(51) 9999", "O nome deve ter no máximo 200 caracteres"),
        ("Loca Sul", "9" * 201, "O contato deve ter no máximo 200 caracteres"),
    ],
)
def test_nome_ou_contato_da_locadora_invalido(nome, contato, mensagem):
    with pytest.raises(TextoInvalido) as erro:
        Locadora.nova(nome, Documento.de("11.222.333/0001-81"), contato)
    assert erro.value.mensagem == mensagem
