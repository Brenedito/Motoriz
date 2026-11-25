"""Casos da suíte de isolamento entre contas.

Cada rota da API precisa de um caso em `CASOS` (a conta A tenta alcançar dados da conta B) ou
estar em `ROTAS_SEM_CONTA`, com o motivo. Cada fatia nova acrescenta os seus casos aqui.

A chave é `(método, caminho da rota como o FastAPI guarda)`, por exemplo
`("POST", "/api/usuarios/{id}/desativar")`. O `caminho` do caso é o que o cliente chama, com os
placeholders `{usuario_b}` (operador da conta B) e `{admin_b}` (admin da conta B).
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from conftest import ContaDaApi
from fastapi.testclient import TestClient


@dataclass(frozen=True)
class Cenario:
    """O que `preparar` e `verificar` enxergam: cada conta com o seu próprio cliente logado."""

    cliente_a: TestClient
    cliente_b: TestClient
    conta_a: ContaDaApi
    conta_b: ContaDaApi


Gancho = Callable[[Cenario], None]


@dataclass(frozen=True)
class CasoDeIsolamento:
    metodo: str
    caminho: str
    corpo: dict | None
    esperado: Literal["404", "lista_sem_dados_de_b"]
    # Roda, como a conta B, antes do ataque da conta A: monta o estado e confirma que há algo
    # de B a proteger (controle positivo).
    preparar: Gancho | None = None
    # Roda, como a conta B, depois do ataque: confirma que os dados de B não mudaram.
    verificar: Gancho | None = None
    # Para listas cujos itens não trazem ids nem e-mails de B (a auditoria os mascara): a
    # resposta inteira precisa vir vazia, senão um vazamento passaria despercebido.
    lista_vazia: bool = False


def _caso(
    metodo: str,
    caminho: str,
    esperado: Literal["404", "lista_sem_dados_de_b"],
    corpo: dict | None = None,
    preparar: Gancho | None = None,
    verificar: Gancho | None = None,
    lista_vazia: bool = False,
) -> CasoDeIsolamento:
    return CasoDeIsolamento(metodo, caminho, corpo, esperado, preparar, verificar, lista_vazia)


def _operador_de_b(c: Cenario) -> dict:
    r = c.cliente_b.get("/api/usuarios")
    assert r.status_code == 200
    achados = [u for u in r.json() if u["id"] == str(c.conta_b.operador_id)]
    assert len(achados) == 1, "o operador de B deveria estar na lista de B"
    return achados[0]


def _b_tem_operador_ativo(c: Cenario) -> None:
    assert _operador_de_b(c)["ativo"] is True


def _b_desativa_operador(c: Cenario) -> None:
    r = c.cliente_b.post(f"/api/usuarios/{c.conta_b.operador_id}/desativar")
    assert r.status_code == 204, r.text
    assert _operador_de_b(c)["ativo"] is False


def _operador_de_b_continua_inativo(c: Cenario) -> None:
    assert _operador_de_b(c)["ativo"] is False


def _b_enxerga_a_propria_trilha(c: Cenario) -> None:
    """Controle positivo: B, que é o dono, vê o registro; sem isso o caso passaria no vazio."""
    r = c.cliente_b.get(f"/api/auditoria?entidade=usuario&entidade_id={c.conta_b.admin_id}")
    assert r.status_code == 200
    assert len(r.json()) >= 1, "B deveria ter registro de auditoria do próprio admin"


CASOS: dict[tuple[str, str], CasoDeIsolamento] = {
    ("GET", "/api/usuarios"): _caso("GET", "/api/usuarios", "lista_sem_dados_de_b"),
    ("POST", "/api/usuarios/{id}/desativar"): _caso(
        "POST",
        "/api/usuarios/{usuario_b}/desativar",
        "404",
        preparar=_b_tem_operador_ativo,
        verificar=_b_tem_operador_ativo,
    ),
    ("POST", "/api/usuarios/{id}/reativar"): _caso(
        "POST",
        "/api/usuarios/{usuario_b}/reativar",
        "404",
        preparar=_b_desativa_operador,
        verificar=_operador_de_b_continua_inativo,
    ),
    # A criação da conta de B já auditou `usuario.criado` para o admin de B: há registro de B
    # que a conta A não pode enxergar.
    ("GET", "/api/auditoria"): _caso(
        "GET",
        "/api/auditoria?entidade=usuario&entidade_id={admin_b}",
        "lista_sem_dados_de_b",
        preparar=_b_enxerga_a_propria_trilha,
        lista_vazia=True,
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
