from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def criar_motor(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def criar_fabrica(motor: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=motor)
