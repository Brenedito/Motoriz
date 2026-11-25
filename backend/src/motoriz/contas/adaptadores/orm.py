from datetime import datetime
from uuid import UUID

from sqlalchemy import CHAR, Boolean, ForeignKey, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from motoriz.infra.banco import Base
from motoriz.infra.conta import DaConta
from motoriz.infra.tipos import DataHoraUTC, UUIDBinario


class LocadoraOrm(Base):
    """A locadora é a própria conta: não é `DaConta`, e o acesso é sempre por id ou documento."""

    __tablename__ = "locadora"

    id: Mapped[UUID] = mapped_column(UUIDBinario, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    documento: Mapped[str] = mapped_column(String(14), unique=True)
    tipo_documento: Mapped[str] = mapped_column(String(4))
    contato: Mapped[str] = mapped_column(String(200))
    situacao: Mapped[str] = mapped_column(String(10))
    criada_em: Mapped[datetime] = mapped_column(DataHoraUTC)


class UsuarioOrm(DaConta, Base):
    __tablename__ = "usuario"
    __table_args__ = (ForeignKeyConstraint(["conta_id"], ["locadora.id"]),)

    id: Mapped[UUID] = mapped_column(UUIDBinario, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    # Único na plataforma inteira: o login acontece antes de se saber a conta.
    email: Mapped[str] = mapped_column(String(254), unique=True)
    papel: Mapped[str] = mapped_column(String(10))
    hash_senha: Mapped[str] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(Boolean)
    versao: Mapped[int] = mapped_column(Integer)
    criado_em: Mapped[datetime] = mapped_column(DataHoraUTC)


class SessaoOrm(DaConta, Base):
    __tablename__ = "sessao"
    __table_args__ = (ForeignKeyConstraint(["conta_id"], ["locadora.id"]),)

    id: Mapped[UUID] = mapped_column(UUIDBinario, primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(UUIDBinario, ForeignKey("usuario.id"), index=True)
    token_hash: Mapped[str] = mapped_column(CHAR(64), unique=True)
    criada_em: Mapped[datetime] = mapped_column(DataHoraUTC)
    expira_em: Mapped[datetime] = mapped_column(DataHoraUTC)
    revogada_em: Mapped[datetime | None] = mapped_column(DataHoraUTC)
