from uuid import UUID

from motoriz.auditoria.api import RegistradorDeAcoes
from motoriz.compartilhado.contexto import ContextoConta, Papel, exigir_papel
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.compartilhado.relogio import Relogio
from motoriz.contas.aplicacao.portas import (
    HasherDeSenha,
    RepositorioLocadoras,
    RepositorioSessoes,
    RepositorioUsuarios,
)
from motoriz.contas.dominio.erros import EmailJaCadastrado
from motoriz.contas.dominio.senha import validar_senha
from motoriz.contas.dominio.usuario import Usuario, verificar_pode_desativar


class CriarUsuario:
    def __init__(
        self, *, usuarios: RepositorioUsuarios, hasher: HasherDeSenha, auditoria: RegistradorDeAcoes
    ) -> None:
        self._usuarios = usuarios
        self._hasher = hasher
        self._auditoria = auditoria

    def executar(
        self, contexto: ContextoConta, nome: str, email: str, papel: Papel, senha_inicial: str
    ) -> Usuario:
        exigir_papel(contexto, Papel.ADMIN)
        endereco = Email.de(email)
        if self._usuarios.email_em_uso(endereco):
            raise EmailJaCadastrado
        validar_senha(senha_inicial)
        usuario = Usuario.novo(
            contexto.conta_id, nome, endereco, papel, self._hasher.gerar(senha_inicial)
        )
        self._usuarios.adicionar(usuario)
        self._auditoria.registrar(
            contexto.ator,
            "usuario.criado",
            "usuario",
            usuario.id,
            depois={
                "nome": usuario.nome,
                "email": usuario.email.valor,
                "papel": usuario.papel.value,
                "ativo": usuario.ativo,
            },
            campos_pessoais=frozenset({"nome", "email"}),
        )
        return usuario


class ListarUsuarios:
    def __init__(self, *, usuarios: RepositorioUsuarios) -> None:
        self._usuarios = usuarios

    def executar(self, contexto: ContextoConta) -> list[Usuario]:
        exigir_papel(contexto, Papel.ADMIN)
        return self._usuarios.listar()


class DesativarUsuario:
    def __init__(
        self,
        *,
        locadoras: RepositorioLocadoras,
        usuarios: RepositorioUsuarios,
        sessoes: RepositorioSessoes,
        relogio: Relogio,
        auditoria: RegistradorDeAcoes,
    ) -> None:
        self._locadoras = locadoras
        self._usuarios = usuarios
        self._sessoes = sessoes
        self._relogio = relogio
        self._auditoria = auditoria

    def executar(self, contexto: ContextoConta, usuario_id: UUID) -> None:
        exigir_papel(contexto, Papel.ADMIN)
        # Uma desativação por vez na conta: sem isso, dois admins que se desativam ao mesmo
        # tempo contariam dois admins ativos cada um, e a conta ficaria sem nenhum.
        self._locadoras.bloquear(contexto.conta_id)
        alvo = self._usuarios.obter(usuario_id, para_alterar=True)
        if alvo is None:
            raise NaoEncontrado("Usuário não encontrado")
        if not alvo.ativo:
            return  # já está desativado: nada muda, e a trilha não ganha registro falso
        verificar_pode_desativar(alvo, contexto.usuario_id, self._usuarios.contar_admins_ativos())
        antes = {"ativo": alvo.ativo}
        alvo.desativar()
        self._usuarios.salvar(alvo)
        self._sessoes.revogar_do_usuario(alvo.id, self._relogio.agora())
        self._auditoria.registrar(
            contexto.ator,
            "usuario.desativado",
            "usuario",
            alvo.id,
            antes=antes,
            depois={"ativo": alvo.ativo},
        )


class ReativarUsuario:
    def __init__(self, *, usuarios: RepositorioUsuarios, auditoria: RegistradorDeAcoes) -> None:
        self._usuarios = usuarios
        self._auditoria = auditoria

    def executar(self, contexto: ContextoConta, usuario_id: UUID) -> None:
        exigir_papel(contexto, Papel.ADMIN)
        alvo = self._usuarios.obter(usuario_id, para_alterar=True)
        if alvo is None:
            raise NaoEncontrado("Usuário não encontrado")
        if alvo.ativo:
            return  # já está ativo: nada muda, e a trilha não ganha registro falso
        antes = {"ativo": alvo.ativo}
        alvo.reativar()
        self._usuarios.salvar(alvo)
        self._auditoria.registrar(
            contexto.ator,
            "usuario.reativado",
            "usuario",
            alvo.id,
            antes=antes,
            depois={"ativo": alvo.ativo},
        )
