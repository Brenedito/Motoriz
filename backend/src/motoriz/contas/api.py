"""Superfície pública do módulo de contas: outros módulos importam só daqui.

Os adaptadores SQL e o hasher também saem por aqui, para a composição da aplicação (HTTP)
montar os casos de uso sem entrar no interior do módulo.
"""

from motoriz.contas.adaptadores.hasher_argon2 import HasherArgon2
from motoriz.contas.adaptadores.repositorios import (
    RepositorioLocadorasSql,
    RepositorioSessoesSql,
    RepositorioUsuariosSql,
)
from motoriz.contas.aplicacao.sessao import (
    AlterarSenha,
    Entrar,
    ResolverSessao,
    Sair,
    SessaoEmitida,
    gerar_hash_ficticio,
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
    SenhaAtualIncorreta,
    SenhaFraca,
    SessaoInvalida,
)
from motoriz.contas.dominio.sessao import DURACAO_SESSAO
from motoriz.contas.dominio.usuario import Usuario

__all__ = [
    "DURACAO_SESSAO",
    "AlterarSenha",
    "CredenciaisInvalidas",
    "CriarLocadora",
    "CriarUsuario",
    "DesativarUsuario",
    "EmailJaCadastrado",
    "Entrar",
    "HasherArgon2",
    "ListarUsuarios",
    "LocadoraCriada",
    "LocadoraJaCadastrada",
    "ReativarLocadora",
    "ReativarUsuario",
    "RepositorioLocadorasSql",
    "RepositorioSessoesSql",
    "RepositorioUsuariosSql",
    "ResolverSessao",
    "Sair",
    "SenhaAtualIncorreta",
    "SenhaFraca",
    "SessaoEmitida",
    "SessaoInvalida",
    "SuspenderLocadora",
    "Usuario",
    "gerar_hash_ficticio",
]
