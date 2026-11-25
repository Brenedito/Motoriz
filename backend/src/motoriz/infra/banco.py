from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from motoriz.infra.conta import instalar_filtro_de_conta

# Nomes determinísticos para índices e restrições: a migração e o ORM usam os mesmos.
CONVENCAO_DE_NOMES = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCAO_DE_NOMES)


def criar_motor(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def criar_fabrica(motor: Engine) -> sessionmaker[Session]:
    fabrica = sessionmaker(bind=motor)
    instalar_filtro_de_conta(fabrica)
    return fabrica
