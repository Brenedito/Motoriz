"""Isolamento por conta (locadora) na aplicação.

O MySQL não tem segurança por linha, então toda tabela de dado de locadora mapeia uma classe
`DaConta` e a sessão aplica, sozinha, o filtro `conta_id = <conta da sessão>`:

- leitura, UPDATE e DELETE pelo ORM recebem o critério da conta (`with_loader_criteria`);
- gravação (flush) recusa objeto `DaConta` de outra conta, olhando o valor atual e o gravado;
- comandos que o critério não alcança — Core sobre `Table` e `insert()` via `Session.execute` —
  são recusados quando tocam tabela da conta;
- sem conta definida, nada que toque `DaConta` roda.

Em todos os casos, a saída é explícita: modo plataforma ou
`execution_options(todas_as_contas=True)` na consulta. SQL textual (`text(...)`) não é analisado e
não deve ser usado para dado de locadora.
"""

from collections.abc import Iterator
from itertools import chain
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import event, inspect
from sqlalchemy.orm import (
    Mapped,
    ORMExecuteState,
    Session,
    UOWTransaction,
    mapped_column,
    sessionmaker,
    with_loader_criteria,
)
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.selectable import TableClause
from sqlalchemy.sql.visitors import ExternallyTraversible, HasTraverseInternals

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


def _entidade_da_conta(elemento: Any) -> bool:
    """O elemento é referência ORM (anotada) a uma entidade `DaConta`?"""
    entidade = getattr(elemento, "_annotations", {}).get("parententity")
    return entidade is not None and issubclass(entidade.mapper.class_, DaConta)


def _da_conta(tabela: Any) -> bool:
    return isinstance(tabela, TableClause) and tabela.name in DaConta._tabelas


def _referencias(comando: ExternallyTraversible) -> Iterator[tuple[bool, bool]]:
    """Percorre o comando e devolve (toca_tabela_da_conta, via_entidade_orm) por referência.

    Não desce dentro de elementos ORM anotados de entidade `DaConta` (entidade, alias, coluna
    mapeada): esses o `with_loader_criteria` filtra. Nas demais entidades desce, porque um
    `aliased(Outra, <subconsulta Core>)` pode esconder tabela da conta. Qualquer `Table`/coluna de
    tabela da conta sem anotação é Core puro, que o critério não alcança.
    """
    pilha: list[Any] = [comando]
    while pilha:
        el = pilha.pop()
        if _entidade_da_conta(el):
            yield True, True
            continue
        if _da_conta(el) or (isinstance(el, ColumnClause) and _da_conta(el.table)):
            yield True, False
        # Só os filhos estruturais: `Select.get_children()` também devolve o FROM derivado das
        # colunas, já sem a anotação ORM, o que faria toda consulta ORM parecer Core.
        if isinstance(el, HasTraverseInternals):
            pilha.extend(HasTraverseInternals.get_children(el))


def _aplicar_filtro(estado: ORMExecuteState) -> None:
    comando = estado.statement
    if not isinstance(comando, ExternallyTraversible):
        return
    refs = list(_referencias(comando))
    toca = bool(refs) or any(issubclass(m.class_, DaConta) for m in estado.all_mappers)
    if not toca:
        return
    if estado.execution_options.get(OPCAO_TODAS_AS_CONTAS):
        return
    info = estado.session.info
    if info.get(CHAVE_PLATAFORMA):
        return
    if estado.is_insert:
        raise ContextoDeContaAusente("INSERT em tabela da conta só pelo flush da sessão")
    if not all(via_orm for _, via_orm in refs) or not estado.is_orm_statement:
        raise ContextoDeContaAusente("Comando Core sobre tabela da conta não é filtrado")
    if not (estado.is_select or estado.is_update or estado.is_delete):
        raise ContextoDeContaAusente("Comando não suportado sobre tabela da conta")
    conta_id = info.get(CHAVE_CONTA)
    if conta_id is None:
        raise ContextoDeContaAusente("Contexto de conta ausente")
    # `conta_id` é uma variável de closure: o SQLAlchemy a rastreia como parâmetro, de modo que
    # o SQL em cache é reaproveitado sem fixar a conta da primeira execução.
    estado.statement = comando.options(
        with_loader_criteria(DaConta, lambda cls: cls.conta_id == conta_id, include_aliases=True)
    )


def _contas_envolvidas(obj: DaConta) -> set[Any]:
    """Conta atual do objeto e, se já gravado, também a conta que está no banco."""
    historico = inspect(obj).attrs.conta_id.history
    return {obj.conta_id, *historico.deleted, *historico.unchanged}


def _verificar_gravacao(sessao: Session, _contexto: UOWTransaction, _instancias: Any) -> None:
    if sessao.info.get(CHAVE_PLATAFORMA):
        return
    conta_id = sessao.info.get(CHAVE_CONTA)
    for obj in chain(sessao.new, sessao.dirty, sessao.deleted):
        if not isinstance(obj, DaConta):
            continue
        if conta_id is None:
            raise ContextoDeContaAusente("Contexto de conta ausente")
        if _contas_envolvidas(obj) != {conta_id}:
            raise ContextoDeContaAusente("Objeto de outra conta")


def instalar_filtro_de_conta(fabrica: sessionmaker[Session]) -> None:
    event.listen(fabrica, "do_orm_execute", _aplicar_filtro)
    event.listen(fabrica, "before_flush", _verificar_gravacao)
