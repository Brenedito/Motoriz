from datetime import datetime
from typing import Protocol
from uuid import UUID

from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.email import Email
from motoriz.contas.dominio.locadora import Locadora
from motoriz.contas.dominio.sessao import Sessao
from motoriz.contas.dominio.usuario import Usuario


class RepositorioLocadoras(Protocol):
    def obter(self, id: UUID) -> Locadora | None: ...

    def obter_por_documento(self, doc: Documento) -> Locadora | None: ...

    def adicionar(self, loc: Locadora) -> None: ...

    def salvar(self, loc: Locadora) -> None: ...


class RepositorioUsuarios(Protocol):
    def obter(self, id: UUID) -> Usuario | None:
        """Só encontra usuários da conta da sessão."""
        ...

    def obter_em_todas_as_contas(self, id: UUID) -> Usuario | None:
        """Para quando a conta ainda não é conhecida (resolver a sessão)."""
        ...

    def obter_por_email_em_todas_as_contas(self, email: Email) -> Usuario | None: ...

    def email_em_uso(self, email: Email) -> bool:
        """Considera todas as contas: o e-mail é único na plataforma."""
        ...

    def listar(self) -> list[Usuario]:
        """Usuários da conta, ordenados por nome."""
        ...

    def contar_admins_ativos(self) -> int: ...

    def adicionar(self, u: Usuario) -> None: ...

    def salvar(self, u: Usuario) -> None: ...


class RepositorioSessoes(Protocol):
    def adicionar(self, s: Sessao) -> None: ...

    def obter_por_hash_em_todas_as_contas(self, token_hash: str) -> Sessao | None: ...

    def salvar(self, s: Sessao) -> None: ...

    def revogar_do_usuario(
        self, usuario_id: UUID, agora: datetime, exceto_hash: str | None = None
    ) -> None:
        """Revoga as sessões abertas do usuário, poupando a de `exceto_hash`, se dada."""
        ...


class HasherDeSenha(Protocol):
    def gerar(self, senha: str) -> str: ...

    def verificar(self, senha: str, hash: str) -> bool: ...
