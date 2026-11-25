from motoriz.compartilhado.documento import Documento
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
