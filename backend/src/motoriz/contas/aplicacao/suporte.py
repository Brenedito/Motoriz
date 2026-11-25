import secrets
from dataclasses import dataclass

from motoriz.auditoria.api import RegistradorDeAcoes
from motoriz.compartilhado.contexto import Ator, Papel
from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.contas.aplicacao.portas import HasherDeSenha, RepositorioLocadoras, RepositorioUsuarios
from motoriz.contas.dominio.erros import EmailJaCadastrado, LocadoraJaCadastrada
from motoriz.contas.dominio.locadora import Locadora, SituacaoLocadora
from motoriz.contas.dominio.usuario import Usuario


def _ator_suporte(locadora: Locadora) -> Ator:
    return Ator(conta_id=locadora.id, usuario_id=None, origem="suporte")


def _campos_pessoais_da_locadora(locadora: Locadora) -> frozenset[str]:
    """O contato é sempre de uma pessoa; numa locadora pessoa física (CPF), nome e documento
    também são dado pessoal e não entram em claro na trilha, que é imutável."""
    if locadora.documento.tipo == "CPF":
        return frozenset({"nome", "documento", "contato"})
    return frozenset({"contato"})


@dataclass(frozen=True)
class LocadoraCriada:
    locadora: Locadora
    admin: Usuario
    senha_inicial: str


class CriarLocadora:
    def __init__(
        self,
        *,
        locadoras: RepositorioLocadoras,
        usuarios: RepositorioUsuarios,
        hasher: HasherDeSenha,
        auditoria: RegistradorDeAcoes,
    ) -> None:
        self._locadoras = locadoras
        self._usuarios = usuarios
        self._hasher = hasher
        self._auditoria = auditoria

    def executar(
        self, nome: str, documento: str, contato: str, admin_nome: str, admin_email: str
    ) -> LocadoraCriada:
        doc = Documento.de(documento)
        email = Email.de(admin_email)
        if self._locadoras.obter_por_documento(doc) is not None:
            raise LocadoraJaCadastrada
        if self._usuarios.email_em_uso(email):
            raise EmailJaCadastrado
        locadora = Locadora.nova(nome, doc, contato)
        senha_inicial = secrets.token_urlsafe(12)  # 16 caracteres
        admin = Usuario.novo(
            locadora.id, admin_nome, email, Papel.ADMIN, self._hasher.gerar(senha_inicial)
        )
        self._locadoras.adicionar(locadora)
        self._usuarios.adicionar(admin)
        ator = _ator_suporte(locadora)
        self._auditoria.registrar(
            ator,
            "locadora.criada",
            "locadora",
            locadora.id,
            depois={
                "nome": locadora.nome,
                "documento": locadora.documento.valor,
                "contato": locadora.contato,
                "situacao": locadora.situacao.value,
            },
            campos_pessoais=_campos_pessoais_da_locadora(locadora),
        )
        self._auditoria.registrar(
            ator,
            "usuario.criado",
            "usuario",
            admin.id,
            depois={
                "nome": admin.nome,
                "email": admin.email.valor,
                "papel": admin.papel.value,
                "ativo": admin.ativo,
            },
            campos_pessoais=frozenset({"nome", "email"}),
        )
        return LocadoraCriada(locadora=locadora, admin=admin, senha_inicial=senha_inicial)


class SuspenderLocadora:
    def __init__(self, *, locadoras: RepositorioLocadoras, auditoria: RegistradorDeAcoes) -> None:
        self._locadoras = locadoras
        self._auditoria = auditoria

    def executar(self, documento: str) -> None:
        locadora = self._locadoras.obter_por_documento(Documento.de(documento))
        if locadora is None:
            raise NaoEncontrado("Locadora não encontrada")
        if locadora.situacao is SituacaoLocadora.SUSPENSA:
            return  # já está suspensa: nada muda, e a trilha não ganha registro falso
        antes = {"situacao": locadora.situacao.value}
        locadora.suspender()
        self._locadoras.salvar(locadora)
        self._auditoria.registrar(
            _ator_suporte(locadora),
            "locadora.suspensa",
            "locadora",
            locadora.id,
            antes=antes,
            depois={"situacao": locadora.situacao.value},
        )


class ReativarLocadora:
    def __init__(self, *, locadoras: RepositorioLocadoras, auditoria: RegistradorDeAcoes) -> None:
        self._locadoras = locadoras
        self._auditoria = auditoria

    def executar(self, documento: str) -> None:
        locadora = self._locadoras.obter_por_documento(Documento.de(documento))
        if locadora is None:
            raise NaoEncontrado("Locadora não encontrada")
        if locadora.situacao is SituacaoLocadora.ATIVA:
            return  # já está ativa: nada muda, e a trilha não ganha registro falso
        antes = {"situacao": locadora.situacao.value}
        locadora.reativar()
        self._locadoras.salvar(locadora)
        self._auditoria.registrar(
            _ator_suporte(locadora),
            "locadora.reativada",
            "locadora",
            locadora.id,
            antes=antes,
            depois={"situacao": locadora.situacao.value},
        )
