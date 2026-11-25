FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Dependências primeiro, para aproveitar o cache de camadas.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src
RUN uv sync --frozen --no-dev

RUN useradd --system --no-create-home motoriz
USER motoriz

EXPOSE 8000

# Migra com o usuário de migração (MOTORIZ_URL_BANCO_MIGRACAO) e só então sobe a API.
CMD ["sh", "-c", "alembic upgrade head && exec fastapi run src/motoriz/app.py --host 0.0.0.0 --port 8000"]
