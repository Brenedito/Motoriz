"""Isolamento por conta (locadora) na aplicação.

O MySQL não tem segurança por linha, então toda tabela de dado de locadora mapeia uma classe
`DaConta` e a sessão aplica, sozinha, o filtro `conta_id = <conta da sessão>`:

- leitura, UPDATE e DELETE pelo ORM recebem o critério da conta (`with_loader_criteria`);
- gravação (flush) recusa objeto `DaConta` de outra conta;
- sem conta definida, nada que toque `DaConta` roda, a não ser em modo plataforma ou com
  `execution_options(todas_as_contas=True)` explícito na consulta.

SQL textual (`text(...)`) e Core puro sobre `Table` não passam pelo filtro: são saídas
deliberadas e não devem ser usados para dado de locadora.
"""

from itertools import chain
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import event
from sqlalchemy.orm import (
    Mapped,
    ORMExecuteState,
    Session,
    UOWTransaction,
    mapped_column,
    sessionmaker,
    with_loader_criteria,
)
from sqlalchemy.sql import visitors
from sqlalchemy.sql.selectable import TableClause

from motoriz.infra.tipos import UUIDBinario

CHAVE_CONTA = "conta_id"
CHAVE_PLATAFORMA = "plataforma"
OPCAO_TODAS_AS_CONTAS = "todas_as_contas"


class ContextoDeContaAusente(RuntimeError):
    pass


class DaConta:
    """Mixin declarativo das tabelas de dado de locadora."""

    _tabelas: ClassVar[set[str]] = set()

    conta_id: Mapped[UUID] = mapped_column(UUIDBinario, nullable=False, index=True)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        tabela = getattr(cls, "__tablename__", None)
        if isinstance(tabela, str):
            DaConta._tabelas.add(tabela)


def definir_conta(sessao: Session, conta_id: UUID) -> None:
    sessao.info.pop(CHAVE_PLATAFORMA, None)
    sessao.info[CHAVE_CONTA] = conta_id


def modo_plataforma(sessao: Session) -> None:
    sessao.info[CHAVE_PLATAFORMA] = True


def _toca_tabela_da_conta(estado: ORMExecuteState) -> bool:
    # `all_mappers` só enxerga as entidades do resultado; `select(func.count()).select_from(X)`,
    # joins e subconsultas ficam de fora. Por isso também percorremos as tabelas do comando.
    if any(issubclass(m.class_, DaConta) for m in estado.all_mappers):
        return True
    comando = estado.statement
    if not isinstance(comando, visitors.ExternallyTraversible):
        return False
    return any(
        isinstance(el, TableClause) and el.name in DaConta._tabelas
        for el in visitors.iterate(comando)
    )


def _aplicar_filtro(estado: ORMExecuteState) -> None:
    if not (estado.is_select or estado.is_update or estado.is_delete):
        return
    if not _toca_tabela_da_conta(estado):
        return
    if estado.execution_options.get(OPCAO_TODAS_AS_CONTAS):
        return
    info = estado.session.info
    if info.get(CHAVE_PLATAFORMA):
        return
    conta_id = info.get(CHAVE_CONTA)
    if conta_id is None:
        raise ContextoDeContaAusente("Contexto de conta ausente")
    # `conta_id` é uma variável de closure: o SQLAlchemy a rastreia como parâmetro, de modo que
    # o SQL em cache é reaproveitado sem fixar a conta da primeira execução.
    estado.statement = estado.statement.options(
        with_loader_criteria(DaConta, lambda cls: cls.conta_id == conta_id, include_aliases=True)
    )


def _verificar_gravacao(sessao: Session, _contexto: UOWTransaction, _instancias: Any) -> None:
    if sessao.info.get(CHAVE_PLATAFORMA):
        return
    conta_id = sessao.info.get(CHAVE_CONTA)
    for obj in chain(sessao.new, sessao.dirty, sessao.deleted):
        if not isinstance(obj, DaConta):
            continue
        if conta_id is None:
            raise ContextoDeContaAusente("Contexto de conta ausente")
        if obj.conta_id != conta_id:
            raise ContextoDeContaAusente("Objeto de outra conta")


def instalar_filtro_de_conta(fabrica: sessionmaker[Session]) -> None:
    event.listen(fabrica, "do_orm_execute", _aplicar_filtro)
    event.listen(fabrica, "before_flush", _verificar_gravacao)
