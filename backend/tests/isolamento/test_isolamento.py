"""A conta A nunca alcança dados da conta B, em nenhuma rota da API."""

from collections.abc import Iterator

import pytest
from conftest import ContaDaApi
from fastapi import FastAPI
from fastapi.testclient import TestClient
from helpers import entrar

from isolamento.casos import CASOS, ROTAS_SEM_CONTA


def _rotas(rotas: list, prefixo: str = "") -> Iterator[tuple[str, str]]:
    """Achata as rotas do app, entrando nos roteadores incluídos (`include_router`)."""
    for rota in rotas:
        if hasattr(rota, "original_router"):
            yield from _rotas(rota.original_router.routes, prefixo + rota.include_context.prefix)
        else:
            for metodo in rota.methods or ():
                if metodo != "HEAD":  # o Starlette acrescenta HEAD a todo GET
                    yield metodo, prefixo + rota.path


def test_toda_rota_tem_caso_de_isolamento(app: FastAPI) -> None:
    rotas = set(_rotas(app.routes))
    assert rotas, "nenhuma rota encontrada: o achatamento das rotas quebrou"
    faltando = rotas - set(CASOS) - ROTAS_SEM_CONTA
    assert not faltando, f"Rotas sem caso de isolamento: {sorted(faltando)}"


def test_casos_e_excecoes_so_citam_rotas_que_existem(app: FastAPI) -> None:
    rotas = set(_rotas(app.routes))
    sobrando = (set(CASOS) | ROTAS_SEM_CONTA) - rotas
    assert not sobrando, f"Rotas citadas que não existem mais: {sorted(sobrando)}"
    assert not set(CASOS) & ROTAS_SEM_CONTA, "rota em CASOS e em ROTAS_SEM_CONTA ao mesmo tempo"


@pytest.mark.parametrize("chave", sorted(CASOS))
def test_conta_a_nao_alcanca_conta_b(
    cliente: TestClient, conta_a: ContaDaApi, conta_b: ContaDaApi, chave: tuple[str, str]
) -> None:
    caso = CASOS[chave]
    entrar(cliente, conta_a.admin_email, "senha-segura-1")
    caminho = caso.caminho.format(usuario_b=conta_b.operador_id, admin_b=conta_b.admin_id)
    r = cliente.request(caso.metodo, caminho, json=caso.corpo)
    if caso.esperado == "404":
        assert r.status_code == 404
        assert str(conta_b.operador_id) not in r.text
    else:
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        for dado in (
            conta_b.admin_id,
            conta_b.admin_email,
            conta_b.operador_id,
            conta_b.operador_email,
        ):
            assert str(dado) not in r.text
