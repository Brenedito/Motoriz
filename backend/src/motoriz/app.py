from fastapi import APIRouter, FastAPI


def criar_app() -> FastAPI:
    app = FastAPI(title="Motoriz", openapi_url="/api/openapi.json", docs_url="/api/docs")
    roteador = APIRouter(prefix="/api")

    @roteador.get("/saude")
    def saude() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(roteador)
    return app
