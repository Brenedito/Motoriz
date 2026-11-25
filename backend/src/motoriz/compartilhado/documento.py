from dataclasses import dataclass
from typing import Literal, Self

from motoriz.compartilhado.erros import ErroDeDominio

_PESOS_CNPJ = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


class DocumentoInvalido(ErroDeDominio):
    def __init__(self, mensagem: str = "CPF ou CNPJ inválido") -> None:
        super().__init__(mensagem)


def _digito_cpf(digitos: str) -> int:
    pesos = range(len(digitos) + 1, 1, -1)
    soma = sum(int(d) * peso for d, peso in zip(digitos, pesos, strict=True))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def _digito_cnpj(digitos: str) -> int:
    pesos = _PESOS_CNPJ[-len(digitos) :]
    resto = sum(int(d) * p for d, p in zip(digitos, pesos, strict=True)) % 11
    return 0 if resto < 2 else 11 - resto


def _cpf_valido(digitos: str) -> bool:
    primeiro = _digito_cpf(digitos[:9])
    segundo = _digito_cpf(digitos[:9] + str(primeiro))
    return digitos[9:] == f"{primeiro}{segundo}"


def _cnpj_valido(digitos: str) -> bool:
    primeiro = _digito_cnpj(digitos[:12])
    segundo = _digito_cnpj(digitos[:12] + str(primeiro))
    return digitos[12:] == f"{primeiro}{segundo}"


@dataclass(frozen=True)
class Documento:
    valor: str
    tipo: Literal["CPF", "CNPJ"]

    @classmethod
    def de(cls, texto: str) -> Self:
        digitos = "".join(c for c in texto if c.isascii() and c.isdigit())
        if len(set(digitos)) <= 1:
            raise DocumentoInvalido
        if len(digitos) == 11 and _cpf_valido(digitos):
            return cls(valor=digitos, tipo="CPF")
        if len(digitos) == 14 and _cnpj_valido(digitos):
            return cls(valor=digitos, tipo="CNPJ")
        raise DocumentoInvalido
