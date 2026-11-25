# Motoriz

Locadoras e donos de frota hoje controlam veículos, contratos, vistorias e manutenções em papel, planilha e WhatsApp. O Motoriz centraliza o ciclo operacional de cada carro (cadastro, locação, vistoria com foto e manutenção) e liga os eventos entre si: locar muda o status do carro, devolver compara a vistoria de saída com a de chegada e o km registrado alimenta o plano de manutenção.

Projeto de portfólio: monólito modular em FastAPI + MySQL, com frontend React PWA.

## Pré-requisitos

- Python 3.13 e [uv](https://docs.astral.sh/uv/)
- Node 22 LTS
- Docker Desktop em execução (MySQL de desenvolvimento e testes de integração com testcontainers)

## Como subir (desenvolvimento)

Na raiz do repositório, suba o MySQL:

```bash
docker compose up -d mysql                 # MySQL de desenvolvimento
```

Backend, a partir de `backend/`:

```bash
uv sync                                    # instala as dependências
uv run alembic upgrade head                # aplica as migrações
uv run fastapi dev src/motoriz/app.py      # API em http://localhost:8000/api
```

Frontend, a partir de `frontend/`:

```bash
npm install
npm run dev                                # http://localhost:5173, com proxy de /api para a API
```

## Rodando tudo com Docker

Na raiz do repositório:

```bash
docker compose up -d --build
```

Sobem o MySQL, a API (que aplica as migrações antes de iniciar) e o frontend servido por nginx. Abra http://localhost:8080; o nginx encaminha `/api/` para a API. Para conferir: `curl http://localhost:8080/api/saude` responde `{"status":"ok"}`.

O MinIO (armazenamento de fotos, ainda sem uso) fica fora do `up` padrão: `docker compose --profile armazenamento up -d`.

Para parar, `docker compose down` (os dados do MySQL ficam no volume; `docker compose down -v` apaga tudo).

### Primeiro acesso

Não há cadastro público. A primeira locadora e o seu administrador saem do comando de suporte, que imprime a senha inicial (troque-a no primeiro acesso):

```bash
# com a stack no ar, na raiz do repositório
docker compose exec api motoriz-suporte criar-locadora \
  --nome "Minha Locadora" --documento 12345678000195 --contato contato@exemplo.com \
  --admin-nome "Ana" --admin-email ana@exemplo.com
```

Em desenvolvimento local (sem Docker para a API), rode o mesmo comando em `backend/` com `uv run motoriz-suporte criar-locadora ...`, com as variáveis do `.env.exemplo` no ambiente. Entre em http://localhost:8080/entrar com o e-mail e a senha impressos.

## Como testar

Em `backend/`:

```bash
uv run pytest            # testes (os marcados com `banco` precisam do Docker)
uv run ruff check .      # lint
uv run ruff format --check .  # formatação
uv run mypy src          # tipos (modo estrito)
uv run lint-imports      # fronteiras entre módulos e camadas
```

Em `frontend/`: `npm test -- --run`, `npm run lint` e `npm run build`. O GitHub Actions (`.github/workflows/ci.yml`) roda tudo isso a cada push e pull request.

## Mapa de `docs/`

- `docs/escopo/`: escopo funcional do MVP (`escopo_Motoriz.md`).
- `docs/superpowers/specs/`: desenho da arquitetura do MVP.
- `docs/superpowers/plans/`: planos de implementação por fatia.
- `docs/adr/`: registros de decisão de arquitetura (ADRs), um por decisão; `0000-modelo.md` é o modelo.
