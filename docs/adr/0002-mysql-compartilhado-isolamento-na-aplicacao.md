# 0002. MySQL compartilhado e isolamento entre locadoras na aplicação

Status: Aceita

## Contexto

Por decisão do autor, todas as locadoras usam um único MySQL (spec §3). O MySQL não tem segurança por linha, então o banco não pode garantir o isolamento entre contas (spec §6.3).

## Decisão

Toda tabela de dado de locadora tem `conta_id`; chaves únicas de negócio e índices começam por `conta_id`. A conta vem sempre da sessão autenticada, nunca do corpo ou da URL. O filtro fica na sessão do banco, não nos repositórios: depois de autenticar, a requisição chama `definir_conta(sessao, conta_id)`, e um evento `do_orm_execute` do SQLAlchemy aplica `with_loader_criteria` a todo modelo `DaConta`; um evento `before_flush` recusa gravar objeto de outra conta. O filtro falha fechado: sem conta definida, nada que toque tabela da conta roda, e comandos que ele não sabe filtrar (Core sobre a tabela, `insert()` via `Session.execute`) são recusados. A saída é sempre explícita: `modo_plataforma(sessao)` para o código de plataforma (login, suporte) ou `execution_options(todas_as_contas=True)` numa consulta específica. Uma suíte de isolamento cria duas contas e tenta ler e alterar dados da outra por cada rota; tudo deve responder 404. IDs são UUIDv7 em `BINARY(16)`, o que evita enumeração.

## Consequências

- O isolamento depende de disciplina e de testes, não do banco.
- Um vazamento entre contas é o pior defeito possível, por isso os testes dedicados são obrigatórios.

## Alternativas

- Um banco ou esquema por locadora: mais isolamento, contra a decisão do autor e mais custo operacional.
- PostgreSQL com row-level security: descartado porque o banco é MySQL por decisão do autor.
