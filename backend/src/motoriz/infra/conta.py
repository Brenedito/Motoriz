"""Isolamento por conta (locadora) na aplicação.

O MySQL não tem segurança por linha, então toda tabela de dado de locadora mapeia uma classe
`DaConta` e a sessão aplica, sozinha, o filtro `conta_id = <conta da sessão>`:

- leitura, UPDATE e DELETE pelo ORM recebem o critério da conta (`with_loader_criteria`);
  recargas de atributo (refresh, expirado, pós-commit) recebem a conta direto no WHERE, porque o
  ORM não aplica o critério nelas;
- `definir_conta` tira do mapa de identidade os objetos de outra conta (`Session.get`);
- gravação (flush) recusa objeto `DaConta` de outra conta, olhando o valor atual e o gravado
  (consultando o banco quando o valor gravado não está carregado);
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

from sqlalchemy import Select, and_, event, inspect, select
from sqlalchemy.orm import (
    Mapped,
    Mapper,
    ORMExecuteState,
    Session,
    UOWTransaction,
    mapped_column,
    sessionmaker,
    with_loader_criteria,
)
from sqlalchemy.sql import visitors
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.selectable import TableClause
from sqlalchemy.sql.visitors import ExternallyTraversible, HasTraverseInternals
from sqlalchemy.util import immutabledict

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
    """Passa a sessão para a conta dada.

    Objetos `DaConta` de outra conta saem do mapa de identidade: senão `Session.get` os
    devolveria sem ir ao banco, escapando do filtro. Objetos expirados (conta desconhecida) só
    saem quando a conta de fato muda. Se algum deles tiver alteração pendente, a troca é
    recusada — descartá-la em silêncio seria pior.
    """
    trocando = sessao.info.get(CHAVE_PLATAFORMA) or sessao.info.get(CHAVE_CONTA) != conta_id
    for obj in list(sessao.identity_map.values()):
        if not isinstance(obj, DaConta):
            continue
        conta_do_objeto = inspect(obj).dict.get("conta_id")
        if conta_do_objeto == conta_id:
            continue
        if conta_do_objeto is None and not trocando:
            # Expirado (ex.: depois de commit) e a conta não mudou: foi carregado nesta conta,
            # e a recarga passa pelo filtro de qualquer forma.
            continue
        if obj in sessao.dirty or obj in sessao.deleted:
            raise ContextoDeContaAusente("Alterações pendentes de outra conta na sessão")
        sessao.expunge(obj)
    sessao.info.pop(CHAVE_PLATAFORMA, None)
    sessao.info[CHAVE_CONTA] = conta_id


def modo_plataforma(sessao: Session) -> None:
    sessao.info[CHAVE_PLATAFORMA] = True


def _entidade_da_conta(elemento: Any) -> Mapper[Any] | None:
    """Mapper da entidade `DaConta` a que o elemento ORM (anotado) se refere, se houver."""
    entidade = getattr(elemento, "_annotations", {}).get("parententity")
    if entidade is None or not issubclass(entidade.mapper.class_, DaConta):
        return None
    mapper: Mapper[Any] = entidade.mapper
    return mapper


def _da_conta(tabela: Any) -> bool:
    return isinstance(tabela, TableClause) and tabela.name in DaConta._tabelas


def _referencias(
    comando: ExternallyTraversible, cobertos: set[int]
) -> Iterator[Mapper[Any] | None]:
    """Percorre o comando e devolve, por referência a tabela da conta, o mapper da entidade ORM
    pela qual ela é feita, ou None se é Core puro.

    Não desce dentro de elementos ORM anotados de entidade `DaConta` (entidade, alias, coluna
    mapeada): esses o `with_loader_criteria` filtra. Nas demais entidades desce, porque um
    `aliased(Outra, <subconsulta Core>)` pode esconder tabela da conta. Qualquer `Table`/coluna de
    tabela da conta sem anotação é Core puro, que o critério não alcança, exceto os elementos em
    `cobertos` (ids de cláusulas internas do ORM; ver `_clausulas_de_identidade`).
    """
    pilha: list[Any] = [comando]
    while pilha:
        el = pilha.pop()
        if id(el) in cobertos:
            continue
        mapper = _entidade_da_conta(el)
        if mapper is not None:
            yield mapper
            continue
        if _da_conta(el) or (isinstance(el, ColumnClause) and _da_conta(el.table)):
            yield None
        # Só os filhos estruturais: `Select.get_children()` também devolve o FROM derivado das
        # colunas, já sem a anotação ORM, o que faria toda consulta ORM parecer Core.
        if isinstance(el, HasTraverseInternals):
            pilha.extend(HasTraverseInternals.get_children(el))


def _mappers_da_conta(estado: ORMExecuteState) -> list[Mapper[Any]]:
    return [m for m in estado.all_mappers if issubclass(m.class_, DaConta)]


def _clausulas_de_identidade(mappers: list[Mapper[Any]]) -> set[int]:
    # `Session.get`, `refresh` e a recarga de atributos expirados montam o WHERE com a própria
    # cláusula de PK do mapper (`mapper._get_clause`), feita de colunas da `Table` sem anotação
    # ORM. Ela vai num SELECT da entidade, que recebe o critério da conta; reconhecemos o objeto
    # exato (por identidade), e não "qualquer coluna da tabela", para não abrir brecha ao Core.
    return {id(m._get_clause[0]) for m in mappers}


def _criterio(conta_id: UUID) -> Any:
    # `conta_id` é uma variável de closure: o SQLAlchemy a rastreia como parâmetro, de modo que
    # o SQL em cache é reaproveitado sem fixar a conta da primeira execução.
    return with_loader_criteria(DaConta, lambda cls: cls.conta_id == conta_id, include_aliases=True)


def _aplicar_filtro(estado: ORMExecuteState) -> Any:
    comando = estado.statement
    if not isinstance(comando, ExternallyTraversible):
        return None
    mappers = _mappers_da_conta(estado)
    refs = list(_referencias(comando, _clausulas_de_identidade(mappers)))
    if not refs and not mappers:
        return None
    if estado.execution_options.get(OPCAO_TODAS_AS_CONTAS):
        return None
    info = estado.session.info
    if info.get(CHAVE_PLATAFORMA):
        return None
    if estado.is_insert:
        raise ContextoDeContaAusente("INSERT em tabela da conta só pelo flush da sessão")
    if any(r is None for r in refs):
        raise ContextoDeContaAusente("Comando Core sobre tabela da conta não é filtrado")
    conta_id = info.get(CHAVE_CONTA)
    if conta_id is None:
        raise ContextoDeContaAusente("Contexto de conta ausente")
    if not estado.is_orm_statement:
        # Só referências ORM, mas o comando ficou sem o plugin ORM — caso de
        # `select(exists().where(Entidade.x == ...))`. Sem o plugin, o critério seria ignorado
        # na compilação; então reexecutamos o comando como ORM, já com o critério.
        sujeito = next((r for r in refs if r is not None), None)
        if not isinstance(comando, Select) or sujeito is None:
            raise ContextoDeContaAusente("Comando não suportado sobre tabela da conta")
        como_orm = _como_orm(comando, sujeito).options(_criterio(conta_id))
        return estado.invoke_statement(statement=como_orm)
    if not (estado.is_select or estado.is_update or estado.is_delete):
        raise ContextoDeContaAusente("Comando não suportado sobre tabela da conta")
    comando = comando.options(_criterio(conta_id))
    if estado.is_select and estado.is_column_load and isinstance(comando, Select):
        # Recarga de atributos (refresh, expirado, pós-commit): o ORM ignora de propósito o
        # `with_loader_criteria` nela (`_for_refresh_state`). Pomos a conta no WHERE à mão; um
        # objeto de outra conta então não volta (ObjectDeletedError).
        for mapper in mappers:
            comando = comando.where(mapper.class_.conta_id == conta_id)
    estado.statement = comando
    return None


def _como_orm(comando: Select[Any], sujeito: Mapper[Any]) -> Select[Any]:
    """Cópia do SELECT, e de todo SELECT aninhado, compilada pelo plugin ORM."""
    plugin = immutabledict({"compile_state_plugin": "orm", "plugin_subject": sujeito})

    def marcar(el: Any) -> None:
        if not el._propagate_attrs.get("compile_state_plugin"):
            el._propagate_attrs = plugin

    copia: Select[Any] = visitors.cloned_traverse(comando, {}, {"select": marcar})
    return copia


def _contas_gravadas(sessao: Session, obj: DaConta) -> set[Any]:
    """Conta que está no banco para o objeto (vazio se ele ainda não foi gravado)."""
    estado = inspect(obj)
    if estado.key is None:
        return set()
    historico = estado.attrs.conta_id.history
    gravadas = {*historico.deleted, *historico.unchanged}
    if gravadas:
        return gravadas
    # `conta_id` não estava carregado quando foi atribuído (ou o objeto expirou): o histórico
    # não sabe o valor antigo, então perguntamos ao banco.
    mapper = estado.mapper
    tabela = mapper.local_table
    condicao = and_(
        *(col == valor for col, valor in zip(mapper.primary_key, estado.key[1], strict=True))
    )
    consulta = select(tabela.c.conta_id).where(condicao)
    return {
        sessao.execute(
            consulta, execution_options={OPCAO_TODAS_AS_CONTAS: True}
        ).scalar_one_or_none()
    }


def _conta_atual(obj: DaConta, gravadas: set[Any]) -> set[Any]:
    estado = inspect(obj)
    if "conta_id" in estado.dict:
        return {estado.dict["conta_id"]}
    return gravadas  # não carregado e não alterado: vale o que está no banco


def _verificar_gravacao(sessao: Session, _contexto: UOWTransaction, _instancias: Any) -> None:
    if sessao.info.get(CHAVE_PLATAFORMA):
        return
    conta_id = sessao.info.get(CHAVE_CONTA)
    for obj in chain(sessao.new, sessao.dirty, sessao.deleted):
        if not isinstance(obj, DaConta):
            continue
        if conta_id is None:
            raise ContextoDeContaAusente("Contexto de conta ausente")
        gravadas = _contas_gravadas(sessao, obj)
        if gravadas | _conta_atual(obj, gravadas) != {conta_id}:
            raise ContextoDeContaAusente("Objeto de outra conta")


def instalar_filtro_de_conta(fabrica: sessionmaker[Session]) -> None:
    event.listen(fabrica, "do_orm_execute", _aplicar_filtro)
    event.listen(fabrica, "before_flush", _verificar_gravacao)
