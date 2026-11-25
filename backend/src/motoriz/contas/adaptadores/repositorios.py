"""Repositórios SQL de contas: convertem modelo ORM <-> entidade do domínio.

Tabelas `DaConta` (usuário, sessão) são lidas sempre por `select`, nunca por `Session.get`: o
`get` devolve o que já estiver no mapa de identidade sem ir ao banco, e com isso escaparia do
filtro de conta.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import func, inspect, select, update
from sqlalchemy.orm import Session

from motoriz.compartilhado.contexto import Papel
from motoriz.compartilhado.documento import Documento
from motoriz.compartilhado.email import Email
from motoriz.compartilhado.erros import NaoEncontrado
from motoriz.compartilhado.relogio import Relogio, RelogioDoSistema
from motoriz.contas.adaptadores.orm import LocadoraOrm, SessaoOrm, UsuarioOrm
from motoriz.contas.dominio.locadora import Locadora, SituacaoLocadora
from motoriz.contas.dominio.sessao import Sessao
from motoriz.contas.dominio.usuario import Usuario
from motoriz.infra.conta import OPCAO_TODAS_AS_CONTAS

_TODAS_AS_CONTAS = {OPCAO_TODAS_AS_CONTAS: True}


# --- Locadoras -------------------------------------------------------------------------------


def _locadora(orm: LocadoraOrm) -> Locadora:
    tipo: Literal["CPF", "CNPJ"] = "CPF" if orm.tipo_documento == "CPF" else "CNPJ"
    return Locadora(
        id=orm.id,
        nome=orm.nome,
        documento=Documento(valor=orm.documento, tipo=tipo),
        contato=orm.contato,
        situacao=SituacaoLocadora(orm.situacao),
    )


class RepositorioLocadorasSql:
    def __init__(self, sessao: Session, relogio: Relogio | None = None) -> None:
        self._sessao = sessao
        self._relogio = relogio or RelogioDoSistema()

    def obter(self, id: UUID) -> Locadora | None:
        orm = self._sessao.get(LocadoraOrm, id)
        return None if orm is None else _locadora(orm)

    def obter_por_documento(self, doc: Documento) -> Locadora | None:
        stmt = select(LocadoraOrm).where(LocadoraOrm.documento == doc.valor)
        orm = self._sessao.scalars(stmt).one_or_none()
        return None if orm is None else _locadora(orm)

    def adicionar(self, loc: Locadora) -> None:
        self._sessao.add(
            LocadoraOrm(
                id=loc.id,
                nome=loc.nome,
                documento=loc.documento.valor,
                tipo_documento=loc.documento.tipo,
                contato=loc.contato,
                situacao=loc.situacao.value,
                criada_em=self._relogio.agora(),
            )
        )
        self._sessao.flush()

    def salvar(self, loc: Locadora) -> None:
        orm = self._sessao.get(LocadoraOrm, loc.id)
        if orm is None:
            raise NaoEncontrado("Locadora não encontrada")
        orm.nome = loc.nome
        orm.documento = loc.documento.valor
        orm.tipo_documento = loc.documento.tipo
        orm.contato = loc.contato
        orm.situacao = loc.situacao.value
        self._sessao.flush()


# --- Usuários --------------------------------------------------------------------------------


def _usuario(orm: UsuarioOrm) -> Usuario:
    return Usuario(
        id=orm.id,
        conta_id=orm.conta_id,
        nome=orm.nome,
        email=Email(valor=orm.email),
        papel=Papel(orm.papel),
        hash_senha=orm.hash_senha,
        ativo=orm.ativo,
    )


class RepositorioUsuariosSql:
    def __init__(self, sessao: Session, relogio: Relogio | None = None) -> None:
        self._sessao = sessao
        self._relogio = relogio or RelogioDoSistema()

    def _orm(self, id: UUID) -> UsuarioOrm | None:
        return self._sessao.scalars(select(UsuarioOrm).where(UsuarioOrm.id == id)).one_or_none()

    def obter(self, id: UUID) -> Usuario | None:
        orm = self._orm(id)
        return None if orm is None else _usuario(orm)

    def obter_em_todas_as_contas(self, id: UUID) -> Usuario | None:
        stmt = select(UsuarioOrm).where(UsuarioOrm.id == id).execution_options(**_TODAS_AS_CONTAS)
        orm = self._sessao.scalars(stmt).one_or_none()
        return None if orm is None else _usuario(orm)

    def obter_por_email_em_todas_as_contas(self, email: Email) -> Usuario | None:
        stmt = (
            select(UsuarioOrm)
            .where(UsuarioOrm.email == email.valor)
            .execution_options(**_TODAS_AS_CONTAS)
        )
        orm = self._sessao.scalars(stmt).one_or_none()
        return None if orm is None else _usuario(orm)

    def email_em_uso(self, email: Email) -> bool:
        stmt = (
            select(UsuarioOrm.id)
            .where(UsuarioOrm.email == email.valor)
            .limit(1)
            .execution_options(**_TODAS_AS_CONTAS)
        )
        return self._sessao.scalar(stmt) is not None

    def listar(self) -> list[Usuario]:
        stmt = select(UsuarioOrm).order_by(UsuarioOrm.nome, UsuarioOrm.id)
        return [_usuario(orm) for orm in self._sessao.scalars(stmt)]

    def contar_admins_ativos(self) -> int:
        stmt = (
            select(func.count())
            .select_from(UsuarioOrm)
            .where(UsuarioOrm.papel == Papel.ADMIN.value, UsuarioOrm.ativo.is_(True))
        )
        return self._sessao.scalar(stmt) or 0

    def adicionar(self, u: Usuario) -> None:
        self._sessao.add(
            UsuarioOrm(
                id=u.id,
                conta_id=u.conta_id,
                nome=u.nome,
                email=u.email.valor,
                papel=u.papel.value,
                hash_senha=u.hash_senha,
                ativo=u.ativo,
                versao=1,
                criado_em=self._relogio.agora(),
            )
        )
        self._sessao.flush()

    def salvar(self, u: Usuario) -> None:
        orm = self._orm(u.id)
        if orm is None:
            raise NaoEncontrado("Usuário não encontrado")
        orm.nome = u.nome
        orm.email = u.email.valor
        orm.papel = u.papel.value
        orm.hash_senha = u.hash_senha
        orm.ativo = u.ativo
        orm.versao += 1
        self._sessao.flush()


# --- Sessões ---------------------------------------------------------------------------------


def _sessao(orm: SessaoOrm) -> Sessao:
    return Sessao(
        id=orm.id,
        conta_id=orm.conta_id,
        usuario_id=orm.usuario_id,
        token_hash=orm.token_hash,
        criada_em=orm.criada_em,
        expira_em=orm.expira_em,
        revogada_em=orm.revogada_em,
    )


class RepositorioSessoesSql:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, s: Sessao) -> None:
        self._sessao.add(
            SessaoOrm(
                id=s.id,
                conta_id=s.conta_id,
                usuario_id=s.usuario_id,
                token_hash=s.token_hash,
                criada_em=s.criada_em,
                expira_em=s.expira_em,
                revogada_em=s.revogada_em,
            )
        )
        self._sessao.flush()

    def obter_por_hash_em_todas_as_contas(self, token_hash: str) -> Sessao | None:
        stmt = (
            select(SessaoOrm)
            .where(SessaoOrm.token_hash == token_hash)
            .execution_options(**_TODAS_AS_CONTAS)
        )
        orm = self._sessao.scalars(stmt).one_or_none()
        return None if orm is None else _sessao(orm)

    def salvar(self, s: Sessao) -> None:
        stmt = select(SessaoOrm).where(SessaoOrm.id == s.id)
        orm = self._sessao.scalars(stmt).one_or_none()
        if orm is None:
            raise NaoEncontrado("Sessão não encontrada")
        orm.expira_em = s.expira_em
        orm.revogada_em = s.revogada_em
        self._sessao.flush()

    def revogar_do_usuario(
        self, usuario_id: UUID, agora: datetime, exceto_hash: str | None = None
    ) -> None:
        condicoes = [SessaoOrm.usuario_id == usuario_id, SessaoOrm.revogada_em.is_(None)]
        if exceto_hash is not None:
            condicoes.append(SessaoOrm.token_hash != exceto_hash)
        stmt = (
            update(SessaoOrm)
            .where(*condicoes)
            .values(revogada_em=agora)
            # "fetch" montaria um SELECT interno com colunas Core, que o filtro de conta recusa;
            # em vez disso, expiramos as sessões já carregadas desse usuário.
            .execution_options(synchronize_session=False)
        )
        self._sessao.execute(stmt)
        for obj in list(self._sessao.identity_map.values()):
            if not isinstance(obj, SessaoOrm):
                continue
            # Lê do estado, sem disparar carga; se o atributo não está carregado, expira também.
            dono = inspect(obj).dict.get("usuario_id")
            if dono is None or dono == usuario_id:
                self._sessao.expire(obj)
