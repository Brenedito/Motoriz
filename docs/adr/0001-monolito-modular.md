# 0001. Monólito modular com domínio isolado

Status: Aceita

## Contexto

O MVP é construído por duas pessoas e precisa mostrar regras de negócio reais com fronteiras claras (spec §4 e §6.1-6.2). As regras (status de veículo, vistoria, vencimento) devem ser testáveis sem infraestrutura.

## Decisão

Um único backend FastAPI dividido em módulos (`contas`, `frota`, `clientes`, `locacao`, `vistoria`, `manutencao`, `alertas`, `consultas`, `auditoria`, `arquivos`). Cada módulo tem `dominio/` (Python puro), `aplicacao/` (casos de uso e portas), `adaptadores/` (SQLAlchemy, rotas, esquemas) e `api.py` (fachada). `dominio` não importa `fastapi`, `sqlalchemy` nem `pydantic`; um módulo só importa outro por `api.py`. Um caso de uso é uma transação; não há eventos assíncronos entre módulos. `alertas` e `consultas` podem ler tabelas alheias por SQL de leitura. As regras são verificadas por `import-linter`.

## Consequências

- Regras de negócio testáveis sem banco nem HTTP.
- Fronteiras visíveis e checadas no CI.
- Mais arquivos e mapeamento entre dataclasses de domínio e modelos SQLAlchemy.

## Alternativas

- FastAPI em camadas tradicionais (rotas, serviços, modelos ORM): mais rápido de escrever, mas acopla regra ao banco e diferencia pouco no portfólio.
- Event sourcing para locação e vistoria: pesado demais para dois construtores.
