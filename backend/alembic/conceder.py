from alembic import op
from sqlalchemy import text


def conceder_app(tabela: str, privilegios: str) -> None:
    """Concede privilégios sobre uma tabela ao usuário da aplicação (motoriz_app)."""
    conexao = op.get_bind()
    schema = conexao.execute(text("SELECT DATABASE()")).scalar_one()
    conexao.execute(text(f"GRANT {privilegios} ON `{schema}`.`{tabela}` TO 'motoriz_app'@'%'"))
