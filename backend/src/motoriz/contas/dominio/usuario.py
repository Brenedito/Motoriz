from dataclasses import dataclass
from typing import Self
from uuid import UUID

from motoriz.compartilhado.contexto import Papel
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import RegraViolada
from motoriz.compartilhado.ids import novo_id
from motoriz.compartilhado.texto import texto_obrigatorio

TAMANHO_MAXIMO_NOME = 200  # coluna `usuario.nome`


@dataclass
class Usuario:
    id: UUID
    conta_id: UUID
    nome: str
    email: Email
    papel: Papel
    hash_senha: str
    ativo: bool

    @classmethod
    def novo(cls, conta_id: UUID, nome: str, email: Email, papel: Papel, hash_senha: str) -> Self:
        return cls(
            id=novo_id(),
            conta_id=conta_id,
            nome=texto_obrigatorio(nome, campo="nome", maximo=TAMANHO_MAXIMO_NOME),
            email=email,
            papel=papel,
            hash_senha=hash_senha,
            ativo=True,
        )

    def desativar(self) -> None:
        self.ativo = False

    def reativar(self) -> None:
        self.ativo = True

    def trocar_hash_senha(self, novo_hash: str) -> None:
        self.hash_senha = novo_hash


def verificar_pode_desativar(alvo: Usuario, autor_id: UUID, admins_ativos: int) -> None:
    if alvo.id == autor_id:
        raise RegraViolada("Você não pode desativar o seu próprio usuário")
    if alvo.papel is Papel.ADMIN and alvo.ativo and admins_ativos <= 1:
        raise RegraViolada("A conta precisa de ao menos um administrador ativo")
