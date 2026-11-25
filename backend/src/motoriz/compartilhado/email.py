from dataclasses import dataclass
from typing import Self

from motoriz.compartilhado.erros import ErroDeDominio


class EmailInvalido(ErroDeDominio):
    def __init__(self, mensagem: str = "E-mail inválido") -> None:
        super().__init__(mensagem)


@dataclass(frozen=True)
class Email:
    valor: str

    @classmethod
    def de(cls, texto: str) -> Self:
        valor = texto.strip().lower()
        if valor.count("@") != 1:
            raise EmailInvalido
        local, dominio = valor.split("@")
        if not local or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
            raise EmailInvalido
        return cls(valor=valor)
