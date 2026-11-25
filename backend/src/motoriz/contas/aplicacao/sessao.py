import secrets
from dataclasses import dataclass
from datetime import datetime

from motoriz.auditoria.api import RegistradorDeAcoes
from motoriz.compartilhado.contexto import Ator, ContextoConta
from motoriz.compartilhado.email import Email, EmailInvalido
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.compartilhado.relogio import Relogio
from motoriz.contas.aplicacao.portas import (
    HasherDeSenha,
    RepositorioLocadoras,
    RepositorioSessoes,
    RepositorioUsuarios,
)
from motoriz.contas.dominio.erros import CredenciaisInvalidas, SessaoInvalida
from motoriz.contas.dominio.senha import TAMANHO_MAXIMO, validar_senha
from motoriz.contas.dominio.sessao import Sessao, hash_token


@dataclass(frozen=True)
class SessaoEmitida:
    token: str
    expira_em: datetime


class Entrar:
    def __init__(
        self,
        *,
        locadoras: RepositorioLocadoras,
        usuarios: RepositorioUsuarios,
        sessoes: RepositorioSessoes,
        hasher: HasherDeSenha,
        relogio: Relogio,
        auditoria: RegistradorDeAcoes,
    ) -> None:
        self._locadoras = locadoras
        self._usuarios = usuarios
        self._sessoes = sessoes
        self._hasher = hasher
        self._relogio = relogio
        self._auditoria = auditoria
        # Hash com o custo real do hasher, para gastar o mesmo tempo quando o e-mail não existe.
        self._hash_ficticio = hasher.gerar(secrets.token_urlsafe(16))

    def executar(self, email: str, senha: str) -> SessaoEmitida:
        # Toda recusa é a mesma exceção, com a mesma mensagem: quem tenta não descobre qual
        # dado falhou. Senha gigante é recusada antes do hasher, para não gastar Argon2 nela.
        if len(senha) > TAMANHO_MAXIMO:
            raise CredenciaisInvalidas
        try:
            endereco = Email.de(email)
        except EmailInvalido:
            raise CredenciaisInvalidas from None
        usuario = self._usuarios.obter_por_email_em_todas_as_contas(endereco)
        if usuario is None:
            self._hasher.verificar(senha, self._hash_ficticio)
            raise CredenciaisInvalidas
        if not self._hasher.verificar(senha, usuario.hash_senha):
            raise CredenciaisInvalidas
        locadora = self._locadoras.obter(usuario.conta_id)
        if not usuario.ativo or locadora is None or not locadora.ativa:
            raise CredenciaisInvalidas
        sessao, token = Sessao.emitir(usuario.conta_id, usuario.id, self._relogio.agora())
        self._sessoes.adicionar(sessao)
        self._auditoria.registrar(
            Ator(conta_id=usuario.conta_id, usuario_id=usuario.id, origem="usuario"),
            "sessao.criada",
            "sessao",
            sessao.id,
        )
        return SessaoEmitida(token=token, expira_em=sessao.expira_em)


class Sair:
    def __init__(
        self, *, sessoes: RepositorioSessoes, relogio: Relogio, auditoria: RegistradorDeAcoes
    ) -> None:
        self._sessoes = sessoes
        self._relogio = relogio
        self._auditoria = auditoria

    def executar(self, token: str) -> None:
        agora = self._relogio.agora()
        sessao = self._sessoes.obter_por_hash_em_todas_as_contas(hash_token(token))
        if sessao is None or not sessao.valida_em(agora):
            return
        sessao.revogar(agora)
        self._sessoes.salvar(sessao)
        self._auditoria.registrar(
            Ator(conta_id=sessao.conta_id, usuario_id=sessao.usuario_id, origem="usuario"),
            "sessao.encerrada",
            "sessao",
            sessao.id,
        )


class ResolverSessao:
    """Roda antes de a conta ser conhecida: só usa as leituras "em todas as contas"."""

    def __init__(
        self,
        *,
        locadoras: RepositorioLocadoras,
        usuarios: RepositorioUsuarios,
        sessoes: RepositorioSessoes,
        relogio: Relogio,
    ) -> None:
        self._locadoras = locadoras
        self._usuarios = usuarios
        self._sessoes = sessoes
        self._relogio = relogio

    def executar(self, token: str | None) -> ContextoConta:
        if not token:
            raise SessaoInvalida
        sessao = self._sessoes.obter_por_hash_em_todas_as_contas(hash_token(token))
        if sessao is None or not sessao.valida_em(self._relogio.agora()):
            raise SessaoInvalida
        usuario = self._usuarios.obter_em_todas_as_contas(sessao.usuario_id)
        if usuario is None or not usuario.ativo:
            raise SessaoInvalida
        locadora = self._locadoras.obter(usuario.conta_id)
        if locadora is None or not locadora.ativa:
            raise SessaoInvalida
        return ContextoConta(conta_id=usuario.conta_id, usuario_id=usuario.id, papel=usuario.papel)


class AlterarSenha:
    def __init__(
        self,
        *,
        usuarios: RepositorioUsuarios,
        sessoes: RepositorioSessoes,
        hasher: HasherDeSenha,
        relogio: Relogio,
        auditoria: RegistradorDeAcoes,
    ) -> None:
        self._usuarios = usuarios
        self._sessoes = sessoes
        self._hasher = hasher
        self._relogio = relogio
        self._auditoria = auditoria

    def executar(
        self, contexto: ContextoConta, token_atual: str, senha_atual: str, senha_nova: str
    ) -> None:
        usuario = self._usuarios.obter(contexto.usuario_id)
        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado")
        if len(senha_atual) > TAMANHO_MAXIMO or not self._hasher.verificar(
            senha_atual, usuario.hash_senha
        ):
            raise CredenciaisInvalidas("Senha atual incorreta.")
        validar_senha(senha_nova)
        usuario.trocar_hash_senha(self._hasher.gerar(senha_nova))
        self._usuarios.salvar(usuario)
        self._sessoes.revogar_do_usuario(
            usuario.id, self._relogio.agora(), exceto_hash=hash_token(token_atual)
        )
        # Sem antes/depois: nem a senha nem o hash vão para a trilha.
        self._auditoria.registrar(contexto.ator, "usuario.senha_alterada", "usuario", usuario.id)
