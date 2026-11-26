from dataclasses import dataclass
from typing import Self

from motoriz.compartilhado.erros import ErroDeDominio

TAMANHO_MAXIMO_EMAIL = 254  # limite do endereço (RFC 5321) e da coluna `usuario.email`


class EmailInvalido(ErroDeDominio):
    def __init__(self, mensagem: str = "E-mail inválido") -> None:
        super().__init__(mensagem)


@dataclass(frozen=True)
class Email:
    valor: str

    @classmethod
    def de(cls, texto: str) -> Self:
        valor = texto.strip().lower()
        if len(valor) > TAMANHO_MAXIMO_EMAIL or valor.count("@") != 1:
            raise EmailInvalido
        if any(c.isspace() for c in valor):
            raise EmailInvalido
        local, dominio = valor.split("@")
        rotulos = dominio.split(".")
        if not local or len(rotulos) < 2 or not all(rotulos):
            raise EmailInvalido  # domínio sem ponto, ou com rótulo vazio ("..", ponto na ponta)
        return cls(valor=valor)
