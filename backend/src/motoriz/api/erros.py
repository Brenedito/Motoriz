"""Erros de domínio -> HTTP, sempre com corpo `{"erro": "<mensagem>"}`."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from motoriz.compartilhado.erros import AcessoNegado, Conflito, ErroDeDominio, NaoEncontrado
from motoriz.contas.api import CredenciaisInvalidas, SessaoInvalida

# Em ordem: vale a primeira classe de que o erro é instância.
_STATUS: tuple[tuple[type[ErroDeDominio], int], ...] = (
    (NaoEncontrado, 404),
    (AcessoNegado, 403),
    (Conflito, 409),
    (CredenciaisInvalidas, 401),
    (SessaoInvalida, 401),
)
_STATUS_PADRAO = 422


def status_do_erro(erro: ErroDeDominio) -> int:
    return next((s for classe, s in _STATUS if isinstance(erro, classe)), _STATUS_PADRAO)


def _campo(local: tuple[int | str, ...]) -> str:
    # ("body", "senha") -> "senha"; ("path", "id") -> "id"; aninhado -> "a.b".
    partes = local[1:] if len(local) > 1 else local
    return ".".join(str(p) for p in partes)


async def _tratar_dominio(_request: Request, erro: Exception) -> JSONResponse:
    assert isinstance(erro, ErroDeDominio)
    return JSONResponse({"erro": erro.mensagem}, status_code=status_do_erro(erro))


async def _tratar_validacao(_request: Request, erro: Exception) -> JSONResponse:
    assert isinstance(erro, RequestValidationError)
    campos = list(dict.fromkeys(_campo(tuple(e["loc"])) for e in erro.errors()))
    return JSONResponse({"erro": "Dados inválidos", "campos": campos}, status_code=422)


def instalar_tratadores(app: FastAPI) -> None:
    app.add_exception_handler(ErroDeDominio, _tratar_dominio)
    app.add_exception_handler(RequestValidationError, _tratar_validacao)
