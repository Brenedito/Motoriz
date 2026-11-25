"""Superfície pública do módulo de contas: outros módulos importam só daqui."""

from motoriz.contas.aplicacao.sessao import (
    AlterarSenha,
    Entrar,
    ResolverSessao,
    Sair,
    SessaoEmitida,
)
from motoriz.contas.aplicacao.suporte import (
    CriarLocadora,
    LocadoraCriada,
    ReativarLocadora,
    SuspenderLocadora,
)
from motoriz.contas.aplicacao.usuarios import (
    CriarUsuario,
    DesativarUsuario,
    ListarUsuarios,
    ReativarUsuario,
)
from motoriz.contas.dominio.erros import (
    CredenciaisInvalidas,
    EmailJaCadastrado,
    LocadoraJaCadastrada,
    SenhaFraca,
    SessaoInvalida,
)

__all__ = [
    "AlterarSenha",
    "CredenciaisInvalidas",
    "CriarLocadora",
    "CriarUsuario",
    "DesativarUsuario",
    "EmailJaCadastrado",
    "Entrar",
    "ListarUsuarios",
    "LocadoraCriada",
    "LocadoraJaCadastrada",
    "ReativarLocadora",
    "ReativarUsuario",
    "ResolverSessao",
    "Sair",
    "SenhaFraca",
    "SessaoEmitida",
    "SessaoInvalida",
    "SuspenderLocadora",
]
