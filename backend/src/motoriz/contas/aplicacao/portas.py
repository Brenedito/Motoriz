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

    def bloquear(self, id: UUID) -> None:
        """Segura a locadora até o fim da transação, serializando as mudanças na conta.

        Quem chega depois espera. Use antes de conferir uma regra que vale para a conta inteira
        (como "ao menos um admin ativo"), para duas requisições não a conferirem ao mesmo tempo.
        """
        ...

    def adicionar(self, loc: Locadora) -> None: ...

    def salvar(self, loc: Locadora) -> None: ...


class RepositorioUsuarios(Protocol):
    def obter(self, id: UUID, *, para_alterar: bool = False) -> Usuario | None:
        """Só encontra usuários da conta da sessão.

        Com `para_alterar`, lê o último estado gravado e segura o usuário até o fim da
        transação, para uma mudança concorrente não se basear em leitura velha.
        """
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

    def contar_admins_ativos(self) -> int:
        """Conta pelo último estado gravado (não por uma foto antiga da transação)."""
        ...

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
