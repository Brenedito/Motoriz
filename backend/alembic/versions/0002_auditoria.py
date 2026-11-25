"""auditoria: trilha de ações imutável

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from conceder import conceder_app
from sqlalchemy.dialects.mysql import DATETIME

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID = sa.BINARY(16)


def upgrade() -> None:
    op.create_table(
        "registro_acao",
        sa.Column("id", ID, nullable=False),
        sa.Column("conta_id", ID, nullable=True),
        sa.Column("usuario_id", ID, nullable=True),
        sa.Column("origem", sa.String(20), nullable=False),
        sa.Column("acao", sa.String(80), nullable=False),
        sa.Column("entidade", sa.String(50), nullable=False),
        sa.Column("entidade_id", ID, nullable=False),
        sa.Column("antes", sa.JSON(), nullable=True),
        sa.Column("depois", sa.JSON(), nullable=True),
        sa.Column("registrado_em", DATETIME(fsp=6), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_registro_acao")),
    )
    op.create_index(
        "ix_registro_acao_trilha",
        "registro_acao",
        ["conta_id", "entidade", "entidade_id", "registrado_em"],
    )
    op.execute(
        "CREATE TRIGGER registro_acao_sem_update BEFORE UPDATE ON registro_acao "
        "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'registro_acao e imutavel'"
    )
    op.execute(
        "CREATE TRIGGER registro_acao_sem_delete BEFORE DELETE ON registro_acao "
        "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'registro_acao e imutavel'"
    )
    # Sem UPDATE nem DELETE: a trilha só cresce (os gatilhos valem também para a migração).
    conceder_app("registro_acao", "SELECT, INSERT")


def downgrade() -> None:
    op.execute("DROP TRIGGER registro_acao_sem_update")
    op.execute("DROP TRIGGER registro_acao_sem_delete")
    op.drop_table("registro_acao")
