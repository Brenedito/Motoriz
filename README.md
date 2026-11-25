# Motoriz

Locadoras e donos de frota hoje controlam veículos, contratos, vistorias e manutenções em papel, planilha e WhatsApp. O Motoriz centraliza o ciclo operacional de cada carro (cadastro, locação, vistoria com foto e manutenção) e liga os eventos entre si: locar muda o status do carro, devolver compara a vistoria de saída com a de chegada e o km registrado alimenta o plano de manutenção.

Projeto de portfólio: monólito modular em FastAPI + MySQL, com frontend React PWA.

## Pré-requisitos

- Python 3.13 e [uv](https://docs.astral.sh/uv/)
- Node 22 LTS
- Docker Desktop em execução (MySQL de desenvolvimento e testes de integração com testcontainers)

## Como subir

Backend, a partir de `backend/`:

```bash
docker compose up -d                       # MySQL (e demais serviços de apoio)
uv sync                                    # instala as dependências
uv run alembic upgrade head                # aplica as migrações
uv run fastapi dev src/motoriz/app.py      # API em http://localhost:8000/api
```

Frontend, a partir de `frontend/`:

```bash
npm install
npm run dev
```

> O `docker compose`, o Alembic e o frontend chegam nas próximas tarefas desta fatia; até lá, só a API de saúde (`GET /api/saude`) responde.

## Como testar

Em `backend/`:

```bash
uv run pytest            # testes (os marcados com `banco` precisam do Docker)
uv run ruff check .      # lint
uv run mypy src          # tipos (modo estrito)
uv run lint-imports      # fronteiras entre módulos e camadas
```

## Mapa de `docs/`

- `docs/escopo/`: escopo funcional do MVP (`escopo_Motoriz.md`).
- `docs/superpowers/specs/`: desenho da arquitetura do MVP.
- `docs/superpowers/plans/`: planos de implementação por fatia.
- `docs/adr/`: registros de decisão de arquitetura (ADRs), um por decisão; `0000-modelo.md` é o modelo.
