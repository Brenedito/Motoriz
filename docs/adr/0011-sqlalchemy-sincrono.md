# 0011. SQLAlchemy síncrono

Status: Aceita

## Contexto

O backend precisa de acesso a MySQL com transações por caso de uso. O volume é pequeno (spec §7).

## Decisão

SQLAlchemy 2.0 síncrono com PyMySQL. O FastAPI executa as rotas síncronas em threadpool. A unidade de trabalho é uma sessão por caso de uso.

## Consequências

- Testes e unidade de trabalho mais simples, sem `async` espalhado.
- Menor vazão por processo que o modo assíncrono, irrelevante nesse volume.
- Trocar para assíncrono depois exigiria reescrever repositórios e testes.

## Alternativas

- SQLAlchemy assíncrono com `aiomysql` ou `asyncmy`: só adiciona complexidade com esse volume.
