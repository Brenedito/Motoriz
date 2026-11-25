from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fakes.auditoria import RegistradorEmMemoria
from fakes.contas import (
    BancoEmMemoria,
    HasherFalso,
    LocadorasEmMemoria,
    SessoesEmMemoria,
    UsuariosEmMemoria,
)

from motoriz.compartilhado.contexto import ContextoConta, Papel
from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.relogio import RelogioFixo
from motoriz.contas.aplicacao.sessao import AlterarSenha, Entrar, ResolverSessao, Sair
from motoriz.contas.aplicacao.suporte import (
    CriarLocadora,
    ReativarLocadora,
    SuspenderLocadora,
)
from motoriz.contas.aplicacao.usuarios import (
    CriarUsuario,
    DesativarUsuario,
    ListarUsuarios,
    ReativarUsuario,
)
from motoriz.contas.dominio.locadora import Locadora
from motoriz.contas.dominio.usuario import Usuario

SENHA = "senha-segura-1"


@dataclass
class Cenario:
    banco: BancoEmMemoria
    relogio: RelogioFixo
    hasher: HasherFalso
    auditoria: RegistradorEmMemoria
    locadoras: LocadorasEmMemoria
    usuarios: UsuariosEmMemoria  # da conta da Ana
    sessoes: SessoesEmMemoria
    locadora: Locadora
    ana: Usuario
    operador: Usuario
    outra_locadora: Locadora
    outro: Usuario
    ctx_admin: ContextoConta
    ctx_operador: ContextoConta
    entrar: Entrar
    sair: Sair
    resolver: ResolverSessao
    alterar_senha: AlterarSenha
    criar: CriarUsuario
    listar: ListarUsuarios
    desativar: DesativarUsuario
    reativar: ReativarUsuario


@dataclass
class CenarioVazio:
    banco: BancoEmMemoria
    relogio: RelogioFixo
    auditoria: RegistradorEmMemoria
    locadoras: LocadorasEmMemoria
    usuarios: UsuariosEmMemoria
    criar_locadora: CriarLocadora
    suspender: SuspenderLocadora
    reativar: ReativarLocadora


def _usuario(conta: UUID, nome: str, email: str, papel: Papel) -> Usuario:
    return Usuario.novo(conta, nome, Email.de(email), papel, "hash:" + SENHA)


@pytest.fixture
def cenario() -> Cenario:
    banco = BancoEmMemoria()
    relogio = RelogioFixo(datetime(2026, 11, 24, 12, 0, tzinfo=UTC))
    hasher = HasherFalso()
    auditoria = RegistradorEmMemoria(relogio)
    locadoras = LocadorasEmMemoria(banco)
    sessoes = SessoesEmMemoria(banco)

    locadora = Locadora.nova("Loca Sul", Documento.de("11.222.333/0001-81"), "(51) 9999")
    outra = Locadora.nova("Loca Norte", Documento.de("11.444.777/0001-61"), "(11) 8888")
    locadoras.adicionar(locadora)
    locadoras.adicionar(outra)

    ana = _usuario(locadora.id, "Ana", "ana@locadora.com", Papel.ADMIN)
    operador = _usuario(locadora.id, "Caio", "caio@locadora.com", Papel.OPERADOR)
    outro = _usuario(outra.id, "Duda", "duda@norte.com", Papel.ADMIN)
    usuarios = UsuariosEmMemoria(locadora.id, banco)
    for u in (ana, operador):
        usuarios.adicionar(u)
    UsuariosEmMemoria(outra.id, banco).adicionar(outro)
    # Entrar e ResolverSessao rodam antes de a conta ser conhecida: repositório sem conta.
    sem_conta = UsuariosEmMemoria(None, banco)

    return Cenario(
        banco=banco,
        relogio=relogio,
        hasher=hasher,
        auditoria=auditoria,
        locadoras=locadoras,
        usuarios=usuarios,
        sessoes=sessoes,
        locadora=locadora,
        ana=ana,
        operador=operador,
        outra_locadora=outra,
        outro=outro,
        ctx_admin=ContextoConta(locadora.id, ana.id, Papel.ADMIN),
        ctx_operador=ContextoConta(locadora.id, operador.id, Papel.OPERADOR),
        entrar=Entrar(
            locadoras=locadoras,
            usuarios=sem_conta,
            sessoes=sessoes,
            hasher=hasher,
            relogio=relogio,
            auditoria=auditoria,
        ),
        sair=Sair(sessoes=sessoes, relogio=relogio, auditoria=auditoria),
        resolver=ResolverSessao(
            locadoras=locadoras, usuarios=sem_conta, sessoes=sessoes, relogio=relogio
        ),
        alterar_senha=AlterarSenha(
            usuarios=usuarios,
            sessoes=sessoes,
            hasher=hasher,
            relogio=relogio,
            auditoria=auditoria,
        ),
        criar=CriarUsuario(usuarios=usuarios, hasher=hasher, auditoria=auditoria),
        listar=ListarUsuarios(usuarios=usuarios),
        desativar=DesativarUsuario(
            locadoras=locadoras,
            usuarios=usuarios,
            sessoes=sessoes,
            relogio=relogio,
            auditoria=auditoria,
        ),
        reativar=ReativarUsuario(usuarios=usuarios, auditoria=auditoria),
    )


@pytest.fixture
def cenario_vazio() -> CenarioVazio:
    banco = BancoEmMemoria()
    relogio = RelogioFixo(datetime(2026, 11, 24, 12, 0, tzinfo=UTC))
    auditoria = RegistradorEmMemoria(relogio)
    locadoras = LocadorasEmMemoria(banco)
    usuarios = UsuariosEmMemoria(None, banco)  # modo plataforma: o Suporte não tem conta
    return CenarioVazio(
        banco=banco,
        relogio=relogio,
        auditoria=auditoria,
        locadoras=locadoras,
        usuarios=usuarios,
        criar_locadora=CriarLocadora(
            locadoras=locadoras, usuarios=usuarios, hasher=HasherFalso(), auditoria=auditoria
        ),
        suspender=SuspenderLocadora(locadoras=locadoras, auditoria=auditoria),
        reativar=ReativarLocadora(locadoras=locadoras, auditoria=auditoria),
    )
