"""Fakes em memória das portas de contas.

Os objetos de domínio são copiados ao gravar e ao ler (`deepcopy`), como numa persistência de
verdade: mudar o objeto em mãos sem chamar `salvar` não altera o que está guardado.
"""

import copy
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from motoriz.compartilhado.contexto import Papel
from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.contas.dominio.locadora import Locadora
from motoriz.contas.dominio.sessao import Sessao
from motoriz.contas.dominio.usuario import Usuario
from motoriz.infra.conta import ContextoDeContaAusente


@dataclass
class BancoEmMemoria:
    """Armazenamento compartilhado entre os fakes, como um único banco de dados."""

    locadoras: dict[UUID, Locadora] = field(default_factory=dict)
    usuarios: dict[UUID, Usuario] = field(default_factory=dict)
    sessoes: dict[UUID, Sessao] = field(default_factory=dict)


class LocadorasEmMemoria:
    def __init__(self, banco: BancoEmMemoria | None = None) -> None:
        self._banco = banco or BancoEmMemoria()
        self.bloqueios: list[UUID] = []  # locadoras bloqueadas, na ordem dos pedidos

    def obter(self, id: UUID) -> Locadora | None:
        return copy.deepcopy(self._banco.locadoras.get(id))

    def bloquear(self, id: UUID) -> None:
        if id not in self._banco.locadoras:
            raise NaoEncontrado("Locadora não encontrada")
        self.bloqueios.append(id)

    def obter_por_documento(self, doc: Documento) -> Locadora | None:
        for loc in self._banco.locadoras.values():
            if loc.documento == doc:
                return copy.deepcopy(loc)
        return None

    def adicionar(self, loc: Locadora) -> None:
        self._banco.locadoras[loc.id] = copy.deepcopy(loc)

    def salvar(self, loc: Locadora) -> None:
        if loc.id not in self._banco.locadoras:
            raise NaoEncontrado("Locadora não encontrada")
        self._banco.locadoras[loc.id] = copy.deepcopy(loc)


class UsuariosEmMemoria:
    """Emula o filtro de conta do repositório SQL.

    `obter`, `listar`, `contar_admins_ativos` e `salvar` só enxergam a conta dada;
    `obter_por_email_em_todas_as_contas`, `obter_em_todas_as_contas` e `email_em_uso` enxergam
    todas. Sem conta (`None`), os métodos filtrados recusam, como a sessão sem conta definida;
    `adicionar` aceita qualquer conta (equivale ao modo plataforma).
    """

    def __init__(self, conta_id: UUID | None, banco: BancoEmMemoria | None = None) -> None:
        self._conta_id = conta_id
        self._banco = banco or BancoEmMemoria()

    def _da_conta(self) -> list[Usuario]:
        if self._conta_id is None:
            raise ContextoDeContaAusente("Contexto de conta ausente")
        return [u for u in self._banco.usuarios.values() if u.conta_id == self._conta_id]

    def obter(self, id: UUID, *, para_alterar: bool = False) -> Usuario | None:
        # Em memória não há foto de transação nem concorrência: `para_alterar` não muda nada.
        for u in self._da_conta():
            if u.id == id:
                return copy.deepcopy(u)
        return None

    def obter_em_todas_as_contas(self, id: UUID) -> Usuario | None:
        return copy.deepcopy(self._banco.usuarios.get(id))

    def obter_por_email_em_todas_as_contas(self, email: Email) -> Usuario | None:
        for u in self._banco.usuarios.values():
            if u.email == email:
                return copy.deepcopy(u)
        return None

    def email_em_uso(self, email: Email) -> bool:
        return any(u.email == email for u in self._banco.usuarios.values())

    def listar(self) -> list[Usuario]:
        return [copy.deepcopy(u) for u in sorted(self._da_conta(), key=lambda u: (u.nome, u.id))]

    def contar_admins_ativos(self) -> int:
        return sum(1 for u in self._da_conta() if u.papel is Papel.ADMIN and u.ativo)

    def adicionar(self, u: Usuario) -> None:
        if self._conta_id is not None and u.conta_id != self._conta_id:
            raise ContextoDeContaAusente("Objeto de outra conta")
        self._banco.usuarios[u.id] = copy.deepcopy(u)

    def salvar(self, u: Usuario) -> None:
        if all(existente.id != u.id for existente in self._da_conta()):
            raise NaoEncontrado("Usuário não encontrado")
        self._banco.usuarios[u.id] = copy.deepcopy(u)


class SessoesEmMemoria:
    def __init__(self, banco: BancoEmMemoria | None = None) -> None:
        self._banco = banco or BancoEmMemoria()

    def adicionar(self, s: Sessao) -> None:
        self._banco.sessoes[s.id] = copy.deepcopy(s)

    def obter_por_hash_em_todas_as_contas(self, token_hash: str) -> Sessao | None:
        for s in self._banco.sessoes.values():
            if s.token_hash == token_hash:
                return copy.deepcopy(s)
        return None

    def salvar(self, s: Sessao) -> None:
        if s.id not in self._banco.sessoes:
            raise NaoEncontrado("Sessão não encontrada")
        self._banco.sessoes[s.id] = copy.deepcopy(s)

    def revogar_do_usuario(
        self, usuario_id: UUID, agora: datetime, exceto_hash: str | None = None
    ) -> None:
        for s in self._banco.sessoes.values():
            if s.usuario_id == usuario_id and s.revogada_em is None and s.token_hash != exceto_hash:
                s.revogar(agora)


class HasherFalso:
    def __init__(self) -> None:
        self.chamadas_verificar = 0

    def gerar(self, senha: str) -> str:
        return "hash:" + senha

    def verificar(self, senha: str, hash: str) -> bool:
        self.chamadas_verificar += 1
        return hash == "hash:" + senha
