# 0011. SQLAlchemy síncrono

Status: Aceita

## Contexto

O backend precisa de acesso a MySQL com transações por caso de uso. O volume é pequeno (spec §7).

## Decisão

SQLAlchemy 2.1 síncrono (fixado em `<2.2`) com PyMySQL. O FastAPI executa as rotas síncronas em threadpool. A unidade de trabalho é uma sessão por caso de uso.

## Consequências

- Testes e unidade de trabalho mais simples, sem `async` espalhado.
- Menor vazão por processo que o modo assíncrono, irrelevante nesse volume.
- Trocar para assíncrono depois exigiria reescrever repositórios e testes.
- O filtro de conta (ADR 0002, `infra/conta.py`) depende de detalhes internos do SQLAlchemy (`mapper._get_clause`, `_propagate_attrs`, a travessia de `HasTraverseInternals`, o tratamento de recargas de atributo). Por isso a versão fica presa em `<2.2`: subir de minor exige rodar a suíte do filtro e a de isolamento antes.

## Alternativas

- SQLAlchemy assíncrono com `aiomysql` ou `asyncmy`: só adiciona complexidade com esse volume.
