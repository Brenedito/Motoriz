from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from motoriz.api.csrf import MiddlewareCsrf
from motoriz.api.erros import instalar_tratadores
from motoriz.auditoria.adaptadores.rotas import roteador as rotas_auditoria
from motoriz.compartilhado.relogio import RelogioDoSistema
from motoriz.contas.adaptadores.rotas import roteador as rotas_contas
from motoriz.contas.api import HasherArgon2, gerar_hash_ficticio
from motoriz.infra.banco import criar_fabrica, criar_motor
from motoriz.infra.config import Configuracao, obter_configuracao


def _ligar_banco(app: FastAPI, config: Configuracao) -> None:
    # `create_engine` não conecta: a primeira conexão só abre na primeira requisição.
    app.state.motor = criar_motor(config.url_banco_app)
    app.state.fabrica = criar_fabrica(app.state.motor)
    app.state.cookie_seguro = config.cookie_seguro


def criar_app(config: Configuracao | None = None) -> FastAPI:
    """Monta a aplicação. Nada aqui abre conexão com o banco.

    Com `config`, o banco é ligado na hora (testes). Sem ela, a configuração só é lida ao
    subir o servidor (lifespan): assim importar o módulo ou exportar o OpenAPI não exige nem
    banco nem variáveis de ambiente.
    """

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        if not hasattr(app.state, "fabrica"):
            _ligar_banco(app, obter_configuracao())
        yield
        app.state.motor.dispose()

    app = FastAPI(
        title="Motoriz",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        lifespan=ciclo_de_vida,
    )
    hasher = HasherArgon2()
    app.state.relogio = RelogioDoSistema()
    app.state.hasher = hasher
    # Uma vez na subida: montar `Entrar` por requisição não gasta um Argon2 a mais.
    app.state.hash_ficticio = gerar_hash_ficticio(hasher)
    if config is not None:
        _ligar_banco(app, config)

    instalar_tratadores(app)
    app.add_middleware(MiddlewareCsrf)

    roteador = APIRouter(prefix="/api")

    @roteador.get("/saude")
    def saude() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(roteador)
    app.include_router(rotas_contas)
    app.include_router(rotas_auditoria)
    return app


# Para `fastapi dev src/motoriz/app.py`. Seguro de importar: não lê configuração nem conecta.
app = criar_app()
