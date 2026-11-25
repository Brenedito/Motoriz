"""Proteção CSRF por cabeçalho próprio.

Um formulário de outro site não consegue enviar cabeçalho customizado, e um `fetch` de outra
origem com ele precisaria passar pelo preflight de CORS, que a API não libera. Somado ao cookie
`SameSite=Strict`, basta exigir `X-Motoriz: 1` em todo método que altera dados.
"""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

CABECALHO = b"x-motoriz"
VALOR = b"1"
METODOS_SEGUROS = frozenset({"GET", "HEAD", "OPTIONS"})


class MiddlewareCsrf:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] not in METODOS_SEGUROS:
            valores = [v for k, v in scope["headers"] if k == CABECALHO]
            if valores != [VALOR]:
                resposta = JSONResponse({"erro": "Requisição não permitida"}, status_code=403)
                await resposta(scope, receive, send)
                return
        await self.app(scope, receive, send)
