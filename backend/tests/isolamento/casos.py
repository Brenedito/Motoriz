"""Casos da suíte de isolamento entre contas.

Cada rota da API precisa de um caso em `CASOS` (a conta A tenta alcançar dados da conta B) ou
estar em `ROTAS_SEM_CONTA`, com o motivo. Cada fatia nova acrescenta os seus casos aqui.

A chave é `(método, caminho da rota como o FastAPI guarda)`, por exemplo
`("POST", "/api/usuarios/{id}/desativar")`. O `caminho` do caso é o que o cliente chama, com os
placeholders `{usuario_b}` (operador da conta B) e `{admin_b}` (admin da conta B).
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class CasoDeIsolamento:
    metodo: str
    caminho: str
    corpo: dict | None
    esperado: Literal["404", "lista_sem_dados_de_b"]


def _caso(
    metodo: str,
    caminho: str,
    esperado: Literal["404", "lista_sem_dados_de_b"],
    corpo: dict | None = None,
) -> CasoDeIsolamento:
    return CasoDeIsolamento(metodo=metodo, caminho=caminho, corpo=corpo, esperado=esperado)


CASOS: dict[tuple[str, str], CasoDeIsolamento] = {
    ("GET", "/api/usuarios"): _caso("GET", "/api/usuarios", "lista_sem_dados_de_b"),
    ("POST", "/api/usuarios/{id}/desativar"): _caso(
        "POST", "/api/usuarios/{usuario_b}/desativar", "404"
    ),
    ("POST", "/api/usuarios/{id}/reativar"): _caso(
        "POST", "/api/usuarios/{usuario_b}/reativar", "404"
    ),
    # A criação da conta de B já auditou `usuario.criado` para o admin de B: há registro de B
    # que a conta A não pode enxergar.
    ("GET", "/api/auditoria"): _caso(
        "GET",
        "/api/auditoria?entidade=usuario&entidade_id={admin_b}",
        "lista_sem_dados_de_b",
    ),
}

ROTAS_SEM_CONTA: set[tuple[str, str]] = {
    # Sessão: só agem sobre o próprio usuário, não recebem id de outra conta.
    ("POST", "/api/sessao"),
    ("GET", "/api/sessao"),
    ("DELETE", "/api/sessao"),
    ("POST", "/api/sessao/senha"),
    ("GET", "/api/saude"),
    # Documentação gerada pelo FastAPI (objetos `Route`, não `APIRoute`).
    ("GET", "/api/openapi.json"),
    ("GET", "/api/docs"),
    ("GET", "/docs/oauth2-redirect"),
    ("GET", "/redoc"),
    # Criar usuário: o corpo não traz id de outra conta (a conta vem da sessão) e o e-mail é
    # único no sistema inteiro, então usar o e-mail de um admin da conta B dá 409, caso já
    # coberto na Task 8. Não há dado de B a alcançar por esta rota.
    ("POST", "/api/usuarios"),
}
