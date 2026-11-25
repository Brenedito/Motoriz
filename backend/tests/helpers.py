"""Ajudantes compartilhados pelos testes (importe com `from helpers import ...`)."""

import random

from fastapi.testclient import TestClient

_PESOS_CNPJ = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def _digito_cnpj(digitos: str) -> str:
    pesos = _PESOS_CNPJ[-len(digitos) :]
    resto = sum(int(d) * p for d, p in zip(digitos, pesos, strict=True)) % 11
    return "0" if resto < 2 else str(11 - resto)


def cnpj_valido_unico() -> str:
    """CNPJ com dígitos verificadores corretos, a partir de 12 dígitos aleatórios."""
    while True:
        base = "".join(random.choices("0123456789", k=12))
        if len(set(base)) > 1:  # todos iguais é recusado pelo `Documento`
            break
    primeiro = _digito_cnpj(base)
    return base + primeiro + _digito_cnpj(base + primeiro)


def entrar(cliente: TestClient, email: str, senha: str) -> None:
    resposta = cliente.post("/api/sessao", json={"email": email, "senha": senha})
    assert resposta.status_code == 204, resposta.text
