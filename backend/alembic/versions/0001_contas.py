"""contas: locadora, usuário e sessão

Revision ID: 0001
Revises:
Create Date: 2026-11-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from conceder import conceder_app
from sqlalchemy.dialects.mysql import DATETIME

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID = sa.BINARY(16)
DATAHORA = DATETIME(fsp=6)


def upgrade() -> None:
    op.create_table(
        "locadora",
        sa.Column("id", ID, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("documento", sa.String(14), nullable=False),
        sa.Column("tipo_documento", sa.String(4), nullable=False),
        sa.Column("contato", sa.String(200), nullable=False),
        sa.Column("situacao", sa.String(10), nullable=False),
        sa.Column("criada_em", DATAHORA, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_locadora")),
        sa.UniqueConstraint("documento", name=op.f("uq_locadora_documento")),
    )
    op.create_table(
        "usuario",
        sa.Column("id", ID, nullable=False),
        sa.Column("conta_id", ID, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("papel", sa.String(10), nullable=False),
        sa.Column("hash_senha", sa.String(255), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.Column("criado_em", DATAHORA, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuario")),
        sa.ForeignKeyConstraint(
            ["conta_id"], ["locadora.id"], name=op.f("fk_usuario_conta_id_locadora")
        ),
        sa.UniqueConstraint("email", name=op.f("uq_usuario_email")),
    )
    op.create_index(op.f("ix_usuario_conta_id"), "usuario", ["conta_id"])
    op.create_table(
        "sessao",
        sa.Column("id", ID, nullable=False),
        sa.Column("conta_id", ID, nullable=False),
        sa.Column("usuario_id", ID, nullable=False),
        sa.Column("token_hash", sa.CHAR(64), nullable=False),
        sa.Column("criada_em", DATAHORA, nullable=False),
        sa.Column("expira_em", DATAHORA, nullable=False),
        sa.Column("revogada_em", DATAHORA, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessao")),
        sa.ForeignKeyConstraint(
            ["conta_id"], ["locadora.id"], name=op.f("fk_sessao_conta_id_locadora")
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuario.id"], name=op.f("fk_sessao_usuario_id_usuario")
        ),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessao_token_hash")),
    )
    op.create_index(op.f("ix_sessao_conta_id"), "sessao", ["conta_id"])
    op.create_index(op.f("ix_sessao_usuario_id"), "sessao", ["usuario_id"])

    # Sem DELETE: nada de contas é apagado.
    for tabela in ("locadora", "usuario", "sessao"):
        conceder_app(tabela, "SELECT, INSERT, UPDATE")


def downgrade() -> None:
    op.drop_table("sessao")
    op.drop_table("usuario")
    op.drop_table("locadora")
