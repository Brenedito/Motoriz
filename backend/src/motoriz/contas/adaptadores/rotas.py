"""Rotas HTTP de contas: montam os repositórios SQL, chamam um caso de uso e convertem a saída.

Regra de negócio não mora aqui; fica nos casos de uso.
"""

from uuid import UUID

from fastapi import APIRouter, Request, Response, status

from motoriz.api.dependencias import COOKIE_SESSAO, Contexto, RelogioDaApi, SessaoBanco
from motoriz.auditoria.api import RegistradorSql
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.contas.adaptadores.esquemas import (
    CorpoAlterarSenha,
    CorpoCriarUsuario,
    CorpoEntrar,
    SessaoAtual,
    UsuarioSaida,
)
from motoriz.contas.adaptadores.repositorios import (
    RepositorioLocadorasSql,
    RepositorioSessoesSql,
    RepositorioUsuariosSql,
)
from motoriz.contas.aplicacao.sessao import AlterarSenha, Entrar, Sair
from motoriz.contas.aplicacao.usuarios import (
    CriarUsuario,
    DesativarUsuario,
    ListarUsuarios,
    ReativarUsuario,
)
from motoriz.contas.dominio.sessao import DURACAO_SESSAO
from motoriz.infra.conta import modo_plataforma

roteador = APIRouter(prefix="/api")


def _gravar_cookie(request: Request, response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE_SESSAO,
        token,
        max_age=int(DURACAO_SESSAO.total_seconds()),
        path="/",
        secure=bool(request.app.state.cookie_seguro),
        httponly=True,
        samesite="strict",
    )


def _apagar_cookie(request: Request, response: Response) -> None:
    response.delete_cookie(
        COOKIE_SESSAO,
        path="/",
        secure=bool(request.app.state.cookie_seguro),
        httponly=True,
        samesite="strict",
    )


# --- Sessão ----------------------------------------------------------------------------------


@roteador.post("/sessao", status_code=status.HTTP_204_NO_CONTENT, tags=["sessao"])
def entrar(
    corpo: CorpoEntrar,
    request: Request,
    response: Response,
    sessao: SessaoBanco,
    relogio: RelogioDaApi,
) -> None:
    modo_plataforma(sessao)  # a conta só é conhecida depois de achar o usuário
    emitida = Entrar(
        locadoras=RepositorioLocadorasSql(sessao, relogio),
        usuarios=RepositorioUsuariosSql(sessao, relogio),
        sessoes=RepositorioSessoesSql(sessao),
        hasher=request.app.state.hasher,
        relogio=relogio,
        auditoria=RegistradorSql(sessao, relogio),
        hash_ficticio=request.app.state.hash_ficticio,
    ).executar(corpo.email, corpo.senha)
    _gravar_cookie(request, response, emitida.token)


@roteador.get("/sessao", tags=["sessao"])
def sessao_atual(contexto: Contexto, sessao: SessaoBanco, relogio: RelogioDaApi) -> SessaoAtual:
    usuario = RepositorioUsuariosSql(sessao, relogio).obter(contexto.usuario_id)
    locadora = RepositorioLocadorasSql(sessao, relogio).obter(contexto.conta_id)
    if usuario is None or locadora is None:  # acabaram de ser lidos por ResolverSessao
        raise NaoEncontrado("Usuário não encontrado")
    return SessaoAtual(
        usuario_id=usuario.id,
        nome=usuario.nome,
        email=usuario.email.valor,
        papel=usuario.papel,
        conta_id=locadora.id,
        conta_nome=locadora.nome,
    )


@roteador.delete("/sessao", status_code=status.HTTP_204_NO_CONTENT, tags=["sessao"])
def sair(request: Request, response: Response, sessao: SessaoBanco, relogio: RelogioDaApi) -> None:
    token = request.cookies.get(COOKIE_SESSAO)
    if token:
        modo_plataforma(sessao)  # a sessão pode ser de qualquer conta
        Sair(
            sessoes=RepositorioSessoesSql(sessao),
            relogio=relogio,
            auditoria=RegistradorSql(sessao, relogio),
        ).executar(token)
    _apagar_cookie(request, response)


@roteador.post("/sessao/senha", status_code=status.HTTP_204_NO_CONTENT, tags=["sessao"])
def alterar_senha(
    corpo: CorpoAlterarSenha,
    request: Request,
    contexto: Contexto,
    sessao: SessaoBanco,
    relogio: RelogioDaApi,
) -> None:
    AlterarSenha(
        usuarios=RepositorioUsuariosSql(sessao, relogio),
        sessoes=RepositorioSessoesSql(sessao),
        hasher=request.app.state.hasher,
        relogio=relogio,
        auditoria=RegistradorSql(sessao, relogio),
    ).executar(
        contexto,
        request.cookies.get(COOKIE_SESSAO, ""),  # obter_contexto já garantiu que existe
        corpo.senha_atual,
        corpo.senha_nova,
    )


# --- Usuários --------------------------------------------------------------------------------


@roteador.get("/usuarios", tags=["usuarios"])
def listar_usuarios(
    contexto: Contexto, sessao: SessaoBanco, relogio: RelogioDaApi
) -> list[UsuarioSaida]:
    usuarios = ListarUsuarios(usuarios=RepositorioUsuariosSql(sessao, relogio)).executar(contexto)
    return [UsuarioSaida.de(u) for u in usuarios]


@roteador.post("/usuarios", status_code=status.HTTP_201_CREATED, tags=["usuarios"])
def criar_usuario(
    corpo: CorpoCriarUsuario,
    request: Request,
    contexto: Contexto,
    sessao: SessaoBanco,
    relogio: RelogioDaApi,
) -> UsuarioSaida:
    usuario = CriarUsuario(
        usuarios=RepositorioUsuariosSql(sessao, relogio),
        hasher=request.app.state.hasher,
        auditoria=RegistradorSql(sessao, relogio),
    ).executar(contexto, corpo.nome, corpo.email, corpo.papel, corpo.senha_inicial)
    return UsuarioSaida.de(usuario)


@roteador.post(
    "/usuarios/{id}/desativar", status_code=status.HTTP_204_NO_CONTENT, tags=["usuarios"]
)
def desativar_usuario(
    id: UUID, contexto: Contexto, sessao: SessaoBanco, relogio: RelogioDaApi
) -> None:
    DesativarUsuario(
        locadoras=RepositorioLocadorasSql(sessao, relogio),
        usuarios=RepositorioUsuariosSql(sessao, relogio),
        sessoes=RepositorioSessoesSql(sessao),
        relogio=relogio,
        auditoria=RegistradorSql(sessao, relogio),
    ).executar(contexto, id)


@roteador.post("/usuarios/{id}/reativar", status_code=status.HTTP_204_NO_CONTENT, tags=["usuarios"])
def reativar_usuario(
    id: UUID, contexto: Contexto, sessao: SessaoBanco, relogio: RelogioDaApi
) -> None:
    ReativarUsuario(
        usuarios=RepositorioUsuariosSql(sessao, relogio),
        auditoria=RegistradorSql(sessao, relogio),
    ).executar(contexto, id)
