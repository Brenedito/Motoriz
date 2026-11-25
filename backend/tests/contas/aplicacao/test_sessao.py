from datetime import timedelta

import pytest
from fakes.contas import HasherFalso, UsuariosEmMemoria

from motoriz.compartilhado.contexto import ContextoConta
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.contas.aplicacao.sessao import Entrar
from motoriz.contas.dominio.erros import (
    CredenciaisInvalidas,
    SenhaAtualIncorreta,
    SenhaFraca,
    SessaoInvalida,
)
from motoriz.contas.dominio.sessao import hash_token

EMAIL = "ana@locadora.com"
SENHA = "senha-segura-1"


def test_entrar_com_email_em_outra_caixa(cenario):
    emitida = cenario.entrar.executar(" ANA@Locadora.com ", SENHA)
    assert emitida.expira_em == cenario.relogio.agora() + timedelta(days=14)
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade) == ("sessao.criada", "sessao")
    assert (r.conta_id, r.usuario_id, r.origem) == (
        cenario.locadora.id,
        cenario.ana.id,
        "usuario",
    )
    sessao = cenario.sessoes.obter_por_hash_em_todas_as_contas(hash_token(emitida.token))
    assert sessao is not None
    assert r.entidade_id == sessao.id


@pytest.mark.parametrize(
    ("email", "senha"),
    [
        (EMAIL, "errada-errada"),
        ("ninguem@x.com", SENHA),
        ("nao-e-email", "x" * 10),
    ],
)
def test_entrar_falha_com_mesma_mensagem(cenario, email, senha):
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar(email, senha)
    assert cenario.auditoria.registros == []


def test_entrar_email_desconhecido_gasta_o_mesmo_hash(cenario):
    # Mesmo custo de Argon2 que um e-mail existente: o tempo não revela quem tem conta.
    antes = cenario.hasher.chamadas_verificar
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar("ninguem@x.com", SENHA)
    assert cenario.hasher.chamadas_verificar - antes == 1


class HasherQueConta(HasherFalso):
    def __init__(self) -> None:
        super().__init__()
        self.gerados = 0
        self.hashes_verificados: list[str] = []

    def gerar(self, senha: str) -> str:
        self.gerados += 1
        return super().gerar(senha)

    def verificar(self, senha: str, hash: str) -> bool:
        self.hashes_verificados.append(hash)
        return super().verificar(senha, hash)


def test_entrar_usa_hash_ficticio_dado_sem_gerar_outro(cenario):
    # A API calcula o hash fictício uma vez na subida: montar Entrar por requisição não pode
    # custar um Argon2 a mais.
    hasher = HasherQueConta()
    entrar = Entrar(
        locadoras=cenario.locadoras,
        usuarios=UsuariosEmMemoria(None, cenario.banco),
        sessoes=cenario.sessoes,
        hasher=hasher,
        relogio=cenario.relogio,
        auditoria=cenario.auditoria,
        hash_ficticio="hash:ficticio-pronto",
    )
    assert hasher.gerados == 0
    with pytest.raises(CredenciaisInvalidas):
        entrar.executar("ninguem@x.com", SENHA)
    assert hasher.hashes_verificados == ["hash:ficticio-pronto"]


def test_entrar_email_malformado_nao_chama_hasher(cenario):
    antes = cenario.hasher.chamadas_verificar
    with pytest.raises(CredenciaisInvalidas):
        cenario.entrar.executar("nao-e-email", SENHA)
    assert cenario.hasher.chamadas_verificar == antes


def test_entrar_senha_gigante_nao_chama_hasher(cenario):
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar(EMAIL, "x" * 129)
    assert cenario.hasher.chamadas_verificar == 0


def test_entrar_bloqueado_para_usuario_inativo(cenario):
    cenario.ana.desativar()
    cenario.usuarios.salvar(cenario.ana)
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar(EMAIL, SENHA)


def test_entrar_bloqueado_para_locadora_suspensa(cenario):
    cenario.locadora.suspender()
    cenario.locadoras.salvar(cenario.locadora)
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar(EMAIL, SENHA)


def test_entrar_bloqueado_quando_locadora_nao_existe(cenario):
    del cenario.banco.locadoras[cenario.locadora.id]
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar(EMAIL, SENHA)


def test_resolver_devolve_o_contexto_da_conta(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    ctx = cenario.resolver.executar(token)
    assert ctx == ContextoConta(cenario.locadora.id, cenario.ana.id, cenario.ana.papel)


def test_resolver_sessao_de_usuario_desativado_falha(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.ana.desativar()
    cenario.usuarios.salvar(cenario.ana)
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)


def test_resolver_sessao_de_locadora_suspensa_falha(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.locadora.suspender()
    cenario.locadoras.salvar(cenario.locadora)
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)


def test_resolver_sessao_expirada_falha(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.relogio.avancar(timedelta(days=14))
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)


def test_resolver_sessao_revogada_falha(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.sair.executar(token)
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)


def test_resolver_sessao_de_usuario_inexistente_falha(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    del cenario.banco.usuarios[cenario.ana.id]
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)


def test_resolver_sessao_de_locadora_inexistente_falha(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    del cenario.banco.locadoras[cenario.locadora.id]
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)


def test_resolver_sem_token_falha(cenario):
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(None)


def test_resolver_token_desconhecido_falha(cenario):
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar("token-que-nao-existe")


def test_sair_revoga_e_audita(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.sair.executar(token)
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade) == ("sessao.encerrada", "sessao")
    assert (r.conta_id, r.usuario_id) == (cenario.locadora.id, cenario.ana.id)
    sessao = cenario.sessoes.obter_por_hash_em_todas_as_contas(hash_token(token))
    assert sessao is not None
    assert sessao.revogada_em == cenario.relogio.agora()
    assert r.entidade_id == sessao.id


def test_sair_sem_sessao_nao_falha_nem_audita(cenario):
    cenario.sair.executar("token-que-nao-existe")
    assert cenario.auditoria.registros == []


def test_sair_duas_vezes_audita_uma(cenario):
    token = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.sair.executar(token)
    cenario.sair.executar(token)
    assert [r.acao for r in cenario.auditoria.registros].count("sessao.encerrada") == 1


def test_alterar_senha_revoga_outras_sessoes_e_mantem_atual(cenario):
    atual = cenario.entrar.executar(EMAIL, SENHA).token
    outra = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.alterar_senha.executar(cenario.ctx_admin, atual, SENHA, "outra-senha-forte")
    assert cenario.resolver.executar(atual).usuario_id == cenario.ana.id
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(outra)
    assert cenario.usuarios.obter(cenario.ana.id).hash_senha == "hash:outra-senha-forte"


def test_alterar_senha_nao_mexe_nas_sessoes_de_outro_usuario(cenario):
    atual = cenario.entrar.executar(EMAIL, SENHA).token
    do_caio = cenario.entrar.executar("caio@locadora.com", SENHA).token
    cenario.alterar_senha.executar(cenario.ctx_admin, atual, SENHA, "outra-senha-forte")
    assert cenario.resolver.executar(do_caio).usuario_id == cenario.operador.id


def test_alterar_senha_audita_sem_valores(cenario):
    atual = cenario.entrar.executar(EMAIL, SENHA).token
    cenario.alterar_senha.executar(cenario.ctx_admin, atual, SENHA, "outra-senha-forte")
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade, r.entidade_id) == (
        "usuario.senha_alterada",
        "usuario",
        cenario.ana.id,
    )
    assert r.antes is None
    assert r.depois is None
    assert r.usuario_id == cenario.ana.id


def test_alterar_senha_com_senha_atual_errada(cenario):
    atual = cenario.entrar.executar(EMAIL, SENHA).token
    # Erro próprio (422), e não CredenciaisInvalidas (401): a sessão continua válida.
    with pytest.raises(SenhaAtualIncorreta, match="Senha atual incorreta."):
        cenario.alterar_senha.executar(
            cenario.ctx_admin, atual, "errada-errada", "outra-senha-forte"
        )
    assert not isinstance(SenhaAtualIncorreta(), CredenciaisInvalidas)
    assert cenario.usuarios.obter(cenario.ana.id).hash_senha == "hash:" + SENHA


def test_alterar_senha_atual_gigante_nao_chama_hasher(cenario):
    atual = cenario.entrar.executar(EMAIL, SENHA).token
    antes = cenario.hasher.chamadas_verificar
    with pytest.raises(SenhaAtualIncorreta):
        cenario.alterar_senha.executar(cenario.ctx_admin, atual, "x" * 129, "outra-senha-forte")
    assert cenario.hasher.chamadas_verificar == antes


def test_alterar_senha_com_nova_fraca(cenario):
    atual = cenario.entrar.executar(EMAIL, SENHA).token
    with pytest.raises(SenhaFraca):
        cenario.alterar_senha.executar(cenario.ctx_admin, atual, SENHA, "curta")
    assert cenario.usuarios.obter(cenario.ana.id).hash_senha == "hash:" + SENHA


def test_alterar_senha_de_usuario_inexistente(cenario):
    ctx = ContextoConta(cenario.locadora.id, cenario.outro.id, cenario.outro.papel)
    with pytest.raises(NaoEncontrado):
        cenario.alterar_senha.executar(ctx, "t", SENHA, "outra-senha-forte")
