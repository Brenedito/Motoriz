"""Corpos de entrada e saída da API de contas.

E-mail e senha chegam como texto livre: a validação (normalização do e-mail, limites da senha)
é do domínio, para dar a mesma mensagem em qualquer porta de entrada.
"""

from uuid import UUID

from pydantic import BaseModel

from motoriz.compartilhado.contexto import Papel
from motoriz.contas.dominio.usuario import Usuario


class CorpoEntrar(BaseModel):
    email: str
    senha: str


class CorpoAlterarSenha(BaseModel):
    senha_atual: str
    senha_nova: str


class SessaoAtual(BaseModel):
    usuario_id: UUID
    nome: str
    email: str
    papel: Papel
    conta_id: UUID
    conta_nome: str


class CorpoCriarUsuario(BaseModel):
    nome: str
    email: str
    papel: Papel
    senha_inicial: str


class UsuarioSaida(BaseModel):
    id: UUID
    nome: str
    email: str
    papel: Papel
    ativo: bool

    @classmethod
    def de(cls, usuario: Usuario) -> "UsuarioSaida":
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email.valor,
            papel=usuario.papel,
            ativo=usuario.ativo,
        )
