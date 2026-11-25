from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from motoriz.infra.banco import Base
from motoriz.infra.tipos import DataHoraUTC, UUIDBinario


class RegistroAcaoOrm(Base):
    """Não é `DaConta`: `conta_id` é anulável (ações de suporte); a consulta filtra por conta."""

    __tablename__ = "registro_acao"
    __table_args__ = (
        Index("ix_registro_acao_trilha", "conta_id", "entidade", "entidade_id", "registrado_em"),
    )

    id: Mapped[UUID] = mapped_column(UUIDBinario, primary_key=True)
    conta_id: Mapped[UUID | None] = mapped_column(UUIDBinario)
    usuario_id: Mapped[UUID | None] = mapped_column(UUIDBinario)
    origem: Mapped[str] = mapped_column(String(20))
    acao: Mapped[str] = mapped_column(String(80))
    entidade: Mapped[str] = mapped_column(String(50))
    entidade_id: Mapped[UUID] = mapped_column(UUIDBinario)
    antes: Mapped[dict[str, object] | None] = mapped_column(JSON)
    depois: Mapped[dict[str, object] | None] = mapped_column(JSON)
    registrado_em: Mapped[datetime] = mapped_column(DataHoraUTC)
