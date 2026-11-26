import re
from dataclasses import dataclass
from typing import Literal, Self

from motoriz.compartilhado.erros import ErroDeDominio

_PESOS_CNPJ = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_MASCARA = re.compile(r"[\s./-]")
_CPF = re.compile(r"[0-9]{11}")
# Desde julho de 2026 o CNPJ pode ter letras nas 12 primeiras posições; os dois dígitos
# verificadores continuam numéricos.
_CNPJ = re.compile(r"[0-9A-Z]{12}[0-9]{2}")


class DocumentoInvalido(ErroDeDominio):
    def __init__(self, mensagem: str = "CPF ou CNPJ inválido") -> None:
        super().__init__(mensagem)


def _digito_cpf(digitos: str) -> int:
    pesos = range(len(digitos) + 1, 1, -1)
    soma = sum(int(d) * peso for d, peso in zip(digitos, pesos, strict=True))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def _digito_cnpj(caracteres: str) -> int:
    # Cada caractere vale o seu código ASCII menos 48: "0".."9" valem 0..9 e "A".."Z", 17..42.
    pesos = _PESOS_CNPJ[-len(caracteres) :]
    resto = sum((ord(c) - 48) * p for c, p in zip(caracteres, pesos, strict=True)) % 11
    return 0 if resto < 2 else 11 - resto


def _cpf_valido(digitos: str) -> bool:
    primeiro = _digito_cpf(digitos[:9])
    segundo = _digito_cpf(digitos[:9] + str(primeiro))
    return digitos[9:] == f"{primeiro}{segundo}"


def _cnpj_valido(caracteres: str) -> bool:
    primeiro = _digito_cnpj(caracteres[:12])
    segundo = _digito_cnpj(caracteres[:12] + str(primeiro))
    return caracteres[12:] == f"{primeiro}{segundo}"


@dataclass(frozen=True)
class Documento:
    valor: str
    tipo: Literal["CPF", "CNPJ"]

    @classmethod
    def de(cls, texto: str) -> Self:
        # Só a máscara (pontos, barra, hífen, espaços) é descartada: qualquer outro caractere
        # torna o documento inválido, em vez de ser engolido em silêncio.
        valor = _MASCARA.sub("", texto).upper()
        if len(set(valor)) <= 1:
            raise DocumentoInvalido
        if _CPF.fullmatch(valor) and _cpf_valido(valor):
            return cls(valor=valor, tipo="CPF")
        if _CNPJ.fullmatch(valor) and _cnpj_valido(valor):
            return cls(valor=valor, tipo="CNPJ")
        raise DocumentoInvalido
