# Fatia 1: Fundação e Contas — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deixar de pé o esqueleto do monólito (backend FastAPI + MySQL + frontend React PWA) com contas de locadora, usuários Admin/Operador, login por sessão, isolamento entre contas e trilha de auditoria imutável — a base de que todas as outras fatias dependem.

**Architecture:** Monólito modular em `backend/src/motoriz/<modulo>/{dominio,aplicacao,adaptadores}` com fachada `api.py` por módulo; regras em Python puro; um caso de uso por requisição HTTP, dentro de uma transação aberta pela dependência do FastAPI. Isolamento por `conta_id` na aplicação com filtro automático do SQLAlchemy; imutabilidade da auditoria garantida por gatilhos e permissões do MySQL.

**Tech Stack:** Python 3.13, FastAPI, Pydantic v2, pydantic-settings, SQLAlchemy 2.0 (síncrono) + PyMySQL, Alembic, argon2-cffi, uuid-utils, uv, ruff, mypy, import-linter, pytest, testcontainers[mysql], httpx; React + TypeScript + Vite, vite-plugin-pwa, React Router, TanStack Query, openapi-fetch/openapi-typescript, Vitest, Testing Library, msw; Docker Compose (MySQL 8.4, MinIO).

**Spec:** `docs/superpowers/specs/2026-11-24-arquitetura-mvp-design.md` (arquitetura) e `docs/escopo/escopo_Motoriz.md` (escopo funcional, após a Task 1).

## Roteiro de fatias do MVP

Cada fatia ganha seu próprio plano quando chegar a vez dela.

1. **Fundação e contas** (este plano).
2. **Frota e arquivos:** veículos, status e histórico de status, leituras de km e correção, armazenamento S3/MinIO com URL assinada e SHA-256.
3. **Clientes:** PF/PJ, CNH, auditoria de leitura de dado pessoal, anonimização.
4. **Vistoria online:** modelos de checklist versionados, checklist, adendo, comparação pura saída × devolução.
5. **Checklist no celular sem conexão:** PWA, IndexedDB, fila de fotos, retomada.
6. **Locação:** rascunho, ativação, devolução, cancelamento, troca de veículo.
7. **Manutenção:** planos, cálculo de vencimento, manutenções, inspeção técnica.
8. **Consultas, alertas e relatórios:** linha do tempo, "quem estava com o carro", painel de alertas, indicadores, PDF da comparação.

## Global Constraints

- Python **3.13**; MySQL **8.4** (InnoDB, `utf8mb4`, `utf8mb4_0900_ai_ci`); Node **22 LTS**.
- Identificadores do domínio em **português sem acento** (`locadora`, `usuario`, `conta_id`); textos exibidos ao usuário em português com acento.
- IDs: **UUIDv7** gerados por `novo_id()`, guardados como `BINARY(16)`.
- Datas/horas: sempre UTC com fuso (`datetime` aware) no Python, `DATETIME(6)` no MySQL; a hora oficial vem do `Relogio` do servidor.
- Toda tabela de dado de locadora tem `conta_id BINARY(16) NOT NULL` e chaves únicas de negócio começam por `conta_id`.
- `dominio/` não importa `fastapi`, `sqlalchemy` nem `pydantic`; um módulo só importa outro por `motoriz.<modulo>.api` (verificado por `lint-imports`).
- Usuário MySQL da aplicação `motoriz_app` recebe privilégios **por tabela**, concedidos nas migrações; migrações rodam como `motoriz_migracao`.
- Rotas sob `/api`; requisições que alteram dados exigem o cabeçalho `X-Motoriz: 1`.
- Cookie de sessão `motoriz_sessao`: `HttpOnly`, `SameSite=Strict`, `Secure` conforme `MOTORIZ_COOKIE_SEGURO` (padrão `true`), duração absoluta de **14 dias**.
- Senha: **10 a 128** caracteres; hash Argon2id.
- Erros → HTTP: `NaoEncontrado` 404, `AcessoNegado` 403, `Conflito` 409, `CredenciaisInvalidas`/`SessaoInvalida` 401, demais `ErroDeDominio` 422. Corpo: `{"erro": "<mensagem>"}`.
- Pré-requisito do ambiente: Docker Desktop rodando (testes de integração usam testcontainers).
- Comandos do backend rodam em `backend/`; do frontend, em `frontend/`.

## Review Focus

1. **E-mail com maiúsculas ou espaços** no cadastro e no login → tratado como o mesmo e-mail (normalizado), inclusive para detectar duplicado. Teste na Task 3 (`Email`) e na Task 8 (login com `" Ana@Locadora.com "`).
2. **Admin desativando a si mesmo ou o último admin ativo** → bloqueado; a conta ficaria sem ninguém para administrá-la. Testes na Task 4 e na Task 8.
3. **Usuário desativado ou locadora suspensa com sessão já aberta** → a próxima requisição recebe 401. Teste na Task 7 (`ResolverSessao`) e na Task 9 (suspender pela CLI e chamar a API).
4. **ID válido de outra locadora** → 404, nunca 403 nem o dado (não revela que existe). Teste na Task 10.
5. **Senha com acentos, emoji ou muito longa** → acentos e emoji aceitos; acima de 128 caracteres recusada com 422, sem gastar Argon2 nela. Teste na Task 4 e na Task 8.

---

### Task 1: Esqueleto do backend, ferramentas e documentação base

**Files:**
- Move: `escopo_Motoriz.md` → `docs/escopo/escopo_Motoriz.md`
- Create: `backend/pyproject.toml`, `backend/src/motoriz/__init__.py`, `backend/src/motoriz/app.py`, `backend/tests/test_saude.py`
- Create: `README.md`, `.gitignore`, `docs/adr/0000-modelo.md`, `docs/adr/0001-monolito-modular.md` … `docs/adr/0012-lgpd-anonimizacao.md`

**Interfaces:**
- Produces: `motoriz.app.criar_app() -> FastAPI` (a Task 8 acrescenta o parâmetro `config`); rota `GET /api/saude` → `{"status": "ok"}`.

- [ ] **Step 1: Mover o escopo e criar o `pyproject.toml`**

`uv init --package --name motoriz` em `backend/`. Dependências e ferramentas listadas no Tech Stack. Configurar no `pyproject.toml`:
- `[tool.ruff]` com `line-length = 100` e regras `E,F,I,B,UP,SIM`;
- `[tool.mypy]` com `strict = true`;
- `[tool.pytest.ini_options]` com `testpaths = ["tests"]`, `markers = ["banco: usa MySQL via testcontainers"]`;
- `[tool.importlinter]` com `root_package = "motoriz"`, `include_external_packages = true` e três contratos:
  - `layers` com `containers = ["motoriz.contas", "motoriz.auditoria"]` e `layers = ["adaptadores", "aplicacao", "dominio"]`;
  - `forbidden`: `motoriz.contas.dominio` e `motoriz.auditoria.dominio` não importam `fastapi`, `sqlalchemy`, `pydantic`;
  - `forbidden`: `motoriz.contas` não importa `motoriz.auditoria.dominio`, `motoriz.auditoria.aplicacao` nem `motoriz.auditoria.adaptadores`.
  Cada fatia nova acrescenta seu módulo nesses contratos.

- [ ] **Step 2: Escrever o teste que falha**

```python
# backend/tests/test_saude.py
from fastapi.testclient import TestClient
from motoriz.app import criar_app

def test_saude_responde_ok():
    resposta = TestClient(criar_app()).get("/api/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `uv run pytest tests/test_saude.py -v`
Expected: FAIL (`ModuleNotFoundError` ou `ImportError` de `criar_app`).

- [ ] **Step 4: Implementar `criar_app() -> FastAPI` em `backend/src/motoriz/app.py`**

`FastAPI(title="Motoriz", openapi_url="/api/openapi.json", docs_url="/api/docs")` com um `APIRouter(prefix="/api")` contendo `GET /saude`.

- [ ] **Step 5: Rodar testes e ferramentas**

Run: `uv run pytest -v; uv run ruff check .; uv run mypy src; uv run lint-imports`
Expected: 1 passed; ruff, mypy e lint-imports sem erros. (Os módulos `contas` e `auditoria` ainda não existem: criar `__init__.py` vazios com as subpastas `dominio/`, `aplicacao/`, `adaptadores/`, para os contratos terem alvo.)

- [ ] **Step 6: Escrever README e ADRs**

`README.md`: o que é o Motoriz (2 frases do escopo), pré-requisitos, como subir (`docker compose up -d`, `uv run alembic upgrade head`, `uv run fastapi dev src/motoriz/app.py`, `npm run dev`), como testar, mapa de `docs/`.
ADRs no formato `0000-modelo.md` (Contexto, Decisão, Consequências, Alternativas), status "Aceita", uma por item: 0001 monólito modular (spec §4 e §6.1-6.2); 0002 MySQL compartilhado e isolamento na aplicação (§3, §6.3); 0003 invariantes no banco com coluna gerada (§6.4); 0004 auditoria imutável por gatilho e permissão (§6.5); 0005 dado pessoal fora da trilha (§6.5); 0006 checklist offline sem conclusão offline (§6.6); 0007 fotos por URL assinada com SHA-256 (§6.7); 0008 sessão opaca em cookie (§6.8); 0009 vencimento persistido e alertas na leitura (§6.9); 0010 comparação congelada e adendos (§6.5, §6.10); 0011 SQLAlchemy síncrono (§7); 0012 anonimização LGPD (§6.12). Cada ADR tem no máximo ~25 linhas e cita a seção da spec.

`.gitignore`: `.venv/`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `node_modules/`, `dist/`, `.env`.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: esqueleto do backend, ferramentas e ADRs da arquitetura"
```

---

### Task 2: Ambiente local, banco e migrações

**Files:**
- Create: `docker-compose.yml`, `infra/mysql/init.sql`
- Create: `backend/src/motoriz/infra/__init__.py`, `backend/src/motoriz/infra/config.py`, `backend/src/motoriz/infra/banco.py`
- Create: `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/conceder.py`, `backend/alembic/versions/` (vazio)
- Create: `backend/tests/conftest.py`, `backend/tests/infra/test_banco.py`
- Create: `.env.exemplo`

**Interfaces:**
- Produces:
  - `motoriz.infra.config.Configuracao(BaseSettings)` com `env_prefix="MOTORIZ_"`, campos `url_banco_app: str`, `url_banco_migracao: str`, `cookie_seguro: bool = True`; `obter_configuracao() -> Configuracao` (cacheada).
  - `motoriz.infra.banco.Base(DeclarativeBase)`; `criar_motor(url: str) -> Engine`; `criar_fabrica(motor: Engine) -> sessionmaker[Session]` (a Task 5 instala nela o filtro de conta).
  - `alembic/conceder.py`: `conceder_app(tabela: str, privilegios: str) -> None` (executa `GRANT <privilegios> ON <schema>.<tabela> TO 'motoriz_app'@'%'`, com o schema lido da conexão).
  - Fixtures em `tests/conftest.py`: `mysql_container` (sessão), `motor_app` (sessão; `Engine` do usuário `motoriz_app`, depois de `alembic upgrade head` como `motoriz_migracao`), `motor_migracao` (sessão), `sessao` (função; `Session` do `motor_app` dentro de uma transação externa desfeita ao final, `join_transaction_mode="create_savepoint"`, criada com `criar_fabrica`).

- [ ] **Step 1: Criar `docker-compose.yml` e `infra/mysql/init.sql`**

`mysql:8.4` na porta 3306, `MYSQL_ROOT_PASSWORD=root_dev`, `MYSQL_DATABASE=motoriz`, comando `--log-bin-trust-function-creators=1 --character-set-server=utf8mb4 --collation-server=utf8mb4_0900_ai_ci`, volume de dados nomeado e `./infra/mysql/init.sql` montado em `/docker-entrypoint-initdb.d/`. `minio/minio` com `server /data --console-address :9001`, portas 9000/9001 (usado a partir da fatia 2).

```sql
-- infra/mysql/init.sql
CREATE USER 'motoriz_migracao'@'%' IDENTIFIED BY 'migracao_dev';
GRANT ALL PRIVILEGES ON motoriz.* TO 'motoriz_migracao'@'%' WITH GRANT OPTION;
CREATE USER 'motoriz_app'@'%' IDENTIFIED BY 'app_dev';
```

`.env.exemplo` com `MOTORIZ_URL_BANCO_APP=mysql+pymysql://motoriz_app:app_dev@localhost:3306/motoriz`, `MOTORIZ_URL_BANCO_MIGRACAO=mysql+pymysql://motoriz_migracao:migracao_dev@localhost:3306/motoriz`, `MOTORIZ_COOKIE_SEGURO=false`.

- [ ] **Step 2: Configurar Alembic**

`alembic/env.py` usa `obter_configuracao().url_banco_migracao`, a menos que `config.get_main_option("sqlalchemy.url")` já esteja definido (os testes definem). `target_metadata = Base.metadata`, importando `motoriz.contas.adaptadores.orm` e `motoriz.auditoria.adaptadores.orm` assim que existirem.

- [ ] **Step 3: Escrever os testes que falham**

```python
# backend/tests/infra/test_banco.py
import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

pytestmark = pytest.mark.banco

def test_usuario_da_aplicacao_conecta(sessao):
    assert sessao.execute(text("SELECT 1")).scalar_one() == 1

def test_usuario_da_aplicacao_nao_cria_tabela(motor_app):
    with motor_app.connect() as conexao, pytest.raises((OperationalError, ProgrammingError)):
        conexao.execute(text("CREATE TABLE intrusa (id INT)"))
```

- [ ] **Step 4: Rodar e ver falhar**

Run: `uv run pytest tests/infra/test_banco.py -v`
Expected: ERROR (fixture `sessao` não encontrada).

- [ ] **Step 5: Implementar `config.py`, `banco.py`, `conceder.py` e as fixtures em `conftest.py`**

`mysql_container`: `MySqlContainer("mysql:8.4", dbname="motoriz")`, `.with_volume_mapping(<caminho absoluto de infra/mysql/init.sql>, "/docker-entrypoint-initdb.d/init.sql")`, `.with_command(<mesmos flags do compose>)`. As URLs dos dois usuários são montadas com o host e a porta expostos. `motor_migracao` roda `alembic.command.upgrade(cfg, "head")` com `cfg.set_main_option("sqlalchemy.url", url_migracao)`.

- [ ] **Step 6: Rodar e ver passar**

Run: `uv run pytest tests/infra -v`
Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: docker compose, configuração, banco e fixtures de MySQL"
```

---

### Task 3: Núcleo compartilhado

**Files:**
- Create: `backend/src/motoriz/compartilhado/__init__.py`, `ids.py`, `relogio.py`, `erros.py`, `documento.py`, `email.py`, `contexto.py`
- Create: `backend/src/motoriz/infra/tipos.py`
- Test: `backend/tests/compartilhado/test_documento.py`, `test_email.py`, `test_contexto.py`, `backend/tests/infra/test_tipos.py`

**Interfaces:**
- Produces:
  - `ids.novo_id() -> uuid.UUID` (UUIDv7 via `uuid_utils.compat.uuid7`).
  - `relogio.Relogio(Protocol)` com `agora() -> datetime`; `RelogioDoSistema` (UTC); `RelogioFixo(instante: datetime)` com `avancar(delta: timedelta) -> None`.
  - `erros`: `ErroDeDominio(Exception)` com atributo `mensagem: str`; subclasses `NaoEncontrado`, `AcessoNegado`, `Conflito`, `RegraViolada`.
  - `documento.Documento` (frozen dataclass, `valor: str` só dígitos, `tipo: Literal["CPF", "CNPJ"]`); `Documento.de(texto: str) -> Documento`; erro `DocumentoInvalido(ErroDeDominio)`.
  - `email.Email` (frozen dataclass, `valor: str`); `Email.de(texto: str) -> Email` (aplica `strip()` e `lower()`, exige exatamente um `@` com texto dos dois lados e um `.` no domínio); erro `EmailInvalido(ErroDeDominio)`.
  - `contexto.Papel(StrEnum)`: `ADMIN = "admin"`, `OPERADOR = "operador"`.
  - `contexto.Ator` (frozen dataclass): `conta_id: UUID | None`, `usuario_id: UUID | None`, `origem: Literal["usuario", "suporte", "sistema"]`.
  - `contexto.ContextoConta` (frozen dataclass): `conta_id: UUID`, `usuario_id: UUID`, `papel: Papel`; propriedade `ator -> Ator` (origem `"usuario"`).
  - `contexto.exigir_papel(contexto: ContextoConta, *papeis: Papel) -> None`, que levanta `AcessoNegado("Ação não permitida para o seu perfil")`.
  - `infra.tipos.UUIDBinario(TypeDecorator[UUID])` com `impl = BINARY(16)`, `cache_ok = True`.

- [ ] **Step 1: Escrever os testes que falham**

```python
# tests/compartilhado/test_documento.py
import pytest
from motoriz.compartilhado.documento import Documento, DocumentoInvalido

def test_cpf_valido_com_mascara():
    d = Documento.de("529.982.247-25")
    assert (d.valor, d.tipo) == ("52998224725", "CPF")

def test_cnpj_valido_com_mascara():
    d = Documento.de("11.222.333/0001-81")
    assert (d.valor, d.tipo) == ("11222333000181", "CNPJ")

@pytest.mark.parametrize("texto", ["529.982.247-26", "111.111.111-11", "11.222.333/0001-80", "123", ""])
def test_documento_invalido(texto):
    with pytest.raises(DocumentoInvalido):
        Documento.de(texto)

# tests/compartilhado/test_email.py
def test_email_normaliza_espacos_e_maiusculas():
    assert Email.de("  Ana@Locadora.COM ").valor == "ana@locadora.com"

@pytest.mark.parametrize("texto", ["ana", "ana@", "@locadora.com", "ana@locadora", "a@@b.com"])
def test_email_invalido(texto):
    with pytest.raises(EmailInvalido):
        Email.de(texto)

# tests/compartilhado/test_contexto.py
def test_exigir_papel_bloqueia_operador():
    ctx = ContextoConta(conta_id=novo_id(), usuario_id=novo_id(), papel=Papel.OPERADOR)
    with pytest.raises(AcessoNegado):
        exigir_papel(ctx, Papel.ADMIN)

def test_exigir_papel_aceita_papel_listado():
    ctx = ContextoConta(conta_id=novo_id(), usuario_id=novo_id(), papel=Papel.ADMIN)
    exigir_papel(ctx, Papel.ADMIN, Papel.OPERADOR)

def test_ids_sao_ordenaveis_no_tempo():
    a, b = novo_id(), novo_id()
    assert a.version == 7 and a < b

# tests/infra/test_tipos.py  (marcado banco)
def test_uuid_binario_ida_e_volta(motor_migracao): ...
```

No `test_uuid_binario_ida_e_volta`, usar `motor_migracao` com `CREATE TEMPORARY TABLE t (id BINARY(16))`, inserir com `UUIDBinario` em `bindparam` e verificar que o valor lido volta como o mesmo `UUID`.

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/compartilhado tests/infra/test_tipos.py -v`
Expected: FAIL (imports inexistentes).

- [ ] **Step 3: Implementar os módulos listados em Interfaces**

`Documento.de` remove tudo que não for dígito; 11 dígitos → CPF, 14 → CNPJ; valida os dígitos verificadores pelos algoritmos oficiais e rejeita sequências repetidas. Mensagem: `"CPF ou CNPJ inválido"`. `EmailInvalido`: `"E-mail inválido"`.

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest tests/compartilhado tests/infra -v`
Expected: todos passam.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: núcleo compartilhado (ids, relógio, erros, documento, e-mail, contexto)"
```

---

### Task 4: Domínio de contas

**Files:**
- Create: `backend/src/motoriz/contas/dominio/locadora.py`, `usuario.py`, `sessao.py`, `senha.py`, `erros.py`
- Test: `backend/tests/contas/dominio/test_locadora.py`, `test_usuario.py`, `test_sessao.py`, `test_senha.py`

**Interfaces:**
- Consumes: Task 3 (`Documento`, `Email`, `Papel`, `ErroDeDominio`, `RegraViolada`, `novo_id`).
- Produces:
  - `SituacaoLocadora(StrEnum)`: `ATIVA = "ativa"`, `SUSPENSA = "suspensa"`.
  - `Locadora` (dataclass): `id: UUID`, `nome: str`, `documento: Documento`, `contato: str`, `situacao: SituacaoLocadora`; `Locadora.nova(nome, documento, contato) -> Locadora`; `suspender() -> None`; `reativar() -> None`; propriedade `ativa -> bool`.
  - `Usuario` (dataclass): `id: UUID`, `conta_id: UUID`, `nome: str`, `email: Email`, `papel: Papel`, `hash_senha: str`, `ativo: bool`; `Usuario.novo(conta_id, nome, email, papel, hash_senha) -> Usuario`; `desativar() -> None`; `reativar() -> None`; `trocar_hash_senha(novo_hash: str) -> None`.
  - `usuario.verificar_pode_desativar(alvo: Usuario, autor_id: UUID, admins_ativos: int) -> None`: levanta `RegraViolada("Você não pode desativar o seu próprio usuário")` se `alvo.id == autor_id`, e `RegraViolada("A conta precisa de ao menos um administrador ativo")` se `alvo` for admin ativo e `admins_ativos <= 1`.
  - `Sessao` (dataclass): `id: UUID`, `conta_id: UUID`, `usuario_id: UUID`, `token_hash: str`, `criada_em: datetime`, `expira_em: datetime`, `revogada_em: datetime | None`; `DURACAO_SESSAO = timedelta(days=14)`; `Sessao.emitir(conta_id, usuario_id, agora) -> tuple[Sessao, str]` (devolve a sessão e o token em claro, `secrets.token_urlsafe(32)`); `hash_token(token: str) -> str` (SHA-256 hex); `valida_em(agora) -> bool`; `revogar(agora) -> None`.
  - `senha.validar_senha(senha: str) -> None`: levanta `SenhaFraca("A senha deve ter entre 10 e 128 caracteres")` fora de 10–128 caracteres (contados com `len`).
  - `erros`: `CredenciaisInvalidas(ErroDeDominio)` com mensagem padrão `"E-mail ou senha incorretos."`; `SessaoInvalida(ErroDeDominio)` com `"Sessão expirada. Entre novamente."`; `SenhaFraca(ErroDeDominio)`; `LocadoraJaCadastrada(Conflito)`; `EmailJaCadastrado(Conflito)` com `"Já existe um usuário com este e-mail"`.

- [ ] **Step 1: Escrever os testes que falham**

```python
def test_nao_pode_desativar_a_si_mesmo():
    admin = usuario(papel=Papel.ADMIN)
    with pytest.raises(RegraViolada, match="próprio usuário"):
        verificar_pode_desativar(admin, autor_id=admin.id, admins_ativos=3)

def test_nao_pode_desativar_ultimo_admin():
    alvo = usuario(papel=Papel.ADMIN)
    with pytest.raises(RegraViolada, match="ao menos um administrador"):
        verificar_pode_desativar(alvo, autor_id=novo_id(), admins_ativos=1)

def test_pode_desativar_operador_mesmo_com_um_admin():
    verificar_pode_desativar(usuario(papel=Papel.OPERADOR), autor_id=novo_id(), admins_ativos=1)

def test_sessao_expira_em_14_dias():
    agora = datetime(2026, 11, 24, 12, tzinfo=UTC)
    sessao, token = Sessao.emitir(novo_id(), novo_id(), agora)
    assert sessao.token_hash == hash_token(token) and token not in sessao.token_hash
    assert sessao.valida_em(agora + timedelta(days=14) - timedelta(seconds=1))
    assert not sessao.valida_em(agora + timedelta(days=14))

def test_sessao_revogada_nao_vale():
    agora = datetime(2026, 11, 24, tzinfo=UTC)
    sessao, _ = Sessao.emitir(novo_id(), novo_id(), agora)
    sessao.revogar(agora)
    assert not sessao.valida_em(agora)

@pytest.mark.parametrize("senha", ["curta", "x" * 129])
def test_senha_fora_do_limite(senha):
    with pytest.raises(SenhaFraca):
        validar_senha(senha)

@pytest.mark.parametrize("senha", ["x" * 10, "x" * 128, "çãoáéíóú🚗🚗", "senha com espaço"])
def test_senha_aceita(senha):
    validar_senha(senha)

def test_locadora_suspensa_e_reativada():
    loc = Locadora.nova("Loca Sul", Documento.de("11.222.333/0001-81"), "(51) 99999-0000")
    assert loc.ativa
    loc.suspender(); assert not loc.ativa
    loc.reativar(); assert loc.ativa
```

(`usuario(...)` é um helper de teste local que chama `Usuario.novo` com valores padrão.)

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/contas/dominio -v`
Expected: FAIL (imports).

- [ ] **Step 3: Implementar os módulos listados em Interfaces**

- [ ] **Step 4: Rodar e ver passar; rodar `lint-imports`**

Run: `uv run pytest tests/contas/dominio -v; uv run lint-imports`
Expected: todos passam; contratos mantidos.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(contas): domínio de locadora, usuário, sessão e senha"
```

---

### Task 5: Persistência de contas e filtro de conta

**Files:**
- Create: `backend/src/motoriz/infra/conta.py`
- Create: `backend/src/motoriz/contas/adaptadores/orm.py`, `repositorios.py`
- Create: `backend/src/motoriz/contas/aplicacao/portas.py`
- Create: `backend/alembic/versions/0001_contas.py`
- Test: `backend/tests/infra/test_filtro_de_conta.py`, `backend/tests/contas/adaptadores/test_repositorios.py`

**Interfaces:**
- Consumes: Task 2 (`Base`, `criar_fabrica`, `conceder_app`, fixtures), Task 3 (`UUIDBinario`), Task 4 (entidades).
- Produces:
  - `infra.conta.DaConta`: mixin declarativo com `conta_id: Mapped[UUID] = mapped_column(UUIDBinario, nullable=False, index=True)`.
  - `infra.conta.instalar_filtro_de_conta(fabrica: sessionmaker[Session]) -> None`:
    - registra `do_orm_execute`: só age quando algum mapper de `orm_execute_state.all_mappers` é subclasse de `DaConta`. SQL textual e tabelas fora da conta passam direto. Nesses casos, se `execution_options` não tiver `todas_as_contas=True`, lê `session.info["conta_id"]` e aplica `with_loader_criteria(DaConta, lambda c: c.conta_id == conta_id, include_aliases=True)`. Sem `conta_id` e sem `session.info.get("plataforma")`, levanta `ContextoDeContaAusente`;
    - registra `before_flush`: todo objeto `DaConta` novo ou alterado precisa ter `conta_id == session.info["conta_id"]`, a menos que `session.info.get("plataforma")`. Caso contrário, levanta `ContextoDeContaAusente("Objeto de outra conta")`.
  - `infra.conta.ContextoDeContaAusente(RuntimeError)`.
  - `infra.conta.definir_conta(sessao: Session, conta_id: UUID) -> None` e `infra.conta.modo_plataforma(sessao: Session) -> None`.
  - `criar_fabrica` (Task 2) passa a chamar `instalar_filtro_de_conta`.
  - Tabelas (migração `0001_contas`):
    - `locadora(id PK, nome VARCHAR(200), documento VARCHAR(14) UNIQUE, tipo_documento VARCHAR(4), contato VARCHAR(200), situacao VARCHAR(10), criada_em DATETIME(6))`;
    - `usuario(id PK, conta_id FK→locadora, nome VARCHAR(200), email VARCHAR(254) UNIQUE, papel VARCHAR(10), hash_senha VARCHAR(255), ativo BOOL, versao INT, criado_em DATETIME(6))`. O e-mail é único na plataforma inteira, porque o login acontece antes de se saber a conta;
    - `sessao(id PK, conta_id FK, usuario_id FK, token_hash CHAR(64) UNIQUE, criada_em, expira_em, revogada_em NULL)`.
    - Grants: `SELECT, INSERT, UPDATE` em `locadora`, `usuario` e `sessao` para `motoriz_app`. Não há `DELETE`: nada de contas é apagado.
  - `aplicacao.portas`:
    - `RepositorioLocadoras(Protocol)`: `obter(id: UUID) -> Locadora | None`; `obter_por_documento(doc: Documento) -> Locadora | None`; `adicionar(loc: Locadora) -> None`; `salvar(loc: Locadora) -> None`.
    - `RepositorioUsuarios(Protocol)`: `obter(id: UUID) -> Usuario | None` (filtrado pela conta); `obter_por_email_em_todas_as_contas(email: Email) -> Usuario | None`; `email_em_uso(email: Email) -> bool` (todas as contas); `listar() -> list[Usuario]` (ordenado por nome); `contar_admins_ativos() -> int`; `adicionar(u: Usuario) -> None`; `salvar(u: Usuario) -> None`.
    - `RepositorioSessoes(Protocol)`: `adicionar(s: Sessao) -> None`; `obter_por_hash_em_todas_as_contas(token_hash: str) -> Sessao | None`; `salvar(s: Sessao) -> None`; `revogar_do_usuario(usuario_id: UUID, agora: datetime) -> None`.
    - `HasherDeSenha(Protocol)`: `gerar(senha: str) -> str`; `verificar(senha: str, hash: str) -> bool`.
  - `adaptadores.repositorios`: `RepositorioLocadorasSql(sessao)`, `RepositorioUsuariosSql(sessao)`, `RepositorioSessoesSql(sessao)`, que convertem modelo ORM ↔ entidade. Os métodos `*_em_todas_as_contas` e `email_em_uso` usam `.execution_options(todas_as_contas=True)`. `locadora` não é `DaConta`: o repositório lê por id.
  - `adaptadores.hasher_argon2.HasherArgon2` (Argon2id, `argon2.PasswordHasher()` padrão).

- [ ] **Step 1: Escrever os testes que falham**

```python
# tests/infra/test_filtro_de_conta.py  (pytestmark banco)
def test_consulta_sem_conta_falha(sessao):
    with pytest.raises(ContextoDeContaAusente):
        sessao.execute(select(UsuarioOrm)).all()

def test_consulta_so_ve_a_propria_conta(sessao, duas_contas):
    a, b = duas_contas            # fixture: cria 2 locadoras com 1 usuário cada, em modo plataforma
    definir_conta(sessao, a.conta_id)
    emails = [u.email for u in sessao.scalars(select(UsuarioOrm))]
    assert emails == [a.email]

def test_gravar_objeto_de_outra_conta_falha(sessao, duas_contas):
    a, b = duas_contas
    definir_conta(sessao, a.conta_id)
    sessao.add(usuario_orm(conta_id=b.conta_id))
    with pytest.raises(ContextoDeContaAusente):
        sessao.flush()

def test_todas_as_contas_e_explicito(sessao, duas_contas):
    definir_conta(sessao, duas_contas[0].conta_id)
    stmt = select(UsuarioOrm).execution_options(todas_as_contas=True)
    assert len(sessao.scalars(stmt).all()) == 2

# tests/contas/adaptadores/test_repositorios.py  (pytestmark banco)
def test_usuario_ida_e_volta(sessao, locadora_gravada): ...
#  adiciona Usuario.novo(...), lê por id, compara todos os campos (email como Email)
def test_email_unico_ignorando_caixa(sessao, locadora_gravada): ...
#  grava ana@x.com; email_em_uso(Email.de("ANA@x.com")) is True
def test_contar_admins_ativos_ignora_inativos(sessao, locadora_gravada): ...
#  2 admins, 1 desativado, 1 operador → 1
def test_revogar_do_usuario_revoga_todas(sessao, locadora_gravada): ...
```

Colocar as fixtures `duas_contas` e `locadora_gravada` em `tests/contas/conftest.py`. Elas gravam em `modo_plataforma` e, para os testes seguintes, voltam a sessão ao estado sem conta (`sessao.info.clear()`).

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/infra/test_filtro_de_conta.py tests/contas/adaptadores -v`
Expected: FAIL/ERROR (módulos e tabelas inexistentes).

- [ ] **Step 3: Implementar `infra/conta.py`, `orm.py`, `portas.py`, `repositorios.py`, `hasher_argon2.py` e a migração `0001_contas.py` (com `conceder_app`)**

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest -v; uv run mypy src; uv run lint-imports`
Expected: tudo passa.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(contas): persistência, filtro automático de conta e migração inicial"
```

---

### Task 6: Auditoria imutável

**Files:**
- Create: `backend/src/motoriz/auditoria/dominio/registro.py`
- Create: `backend/src/motoriz/auditoria/aplicacao/portas.py`, `consultar.py`
- Create: `backend/src/motoriz/auditoria/adaptadores/orm.py`, `registrador_sql.py`
- Create: `backend/src/motoriz/auditoria/api.py`
- Create: `backend/alembic/versions/0002_auditoria.py`
- Create: `backend/tests/fakes/__init__.py`, `backend/tests/fakes/auditoria.py`
- Test: `backend/tests/auditoria/test_registro.py`, `backend/tests/auditoria/test_registrador_sql.py`, `backend/tests/auditoria/test_imutabilidade.py`

**Interfaces:**
- Consumes: Task 3 (`Ator`, `ContextoConta`, `Relogio`, `novo_id`, `UUIDBinario`). `registro_acao` **não** usa `DaConta`, porque `conta_id` é anulável (ações de suporte); a consulta filtra por conta explicitamente.
- Produces:
  - `dominio.registro.MARCADOR_PESSOAL = "[dado pessoal]"`.
  - `dominio.registro.RegistroDeAcao` (frozen dataclass): `id, conta_id: UUID | None, usuario_id: UUID | None, origem: str, acao: str, entidade: str, entidade_id: UUID, antes: dict[str, object] | None, depois: dict[str, object] | None, registrado_em: datetime`.
  - `dominio.registro.mascarar(dados: Mapping[str, object] | None, campos_pessoais: frozenset[str]) -> dict[str, object] | None`: troca o valor de cada campo pessoal presente por `MARCADOR_PESSOAL`; não altera o dicionário recebido.
  - `aplicacao.portas.RegistradorDeAcoes(Protocol)`: `registrar(ator: Ator, acao: str, entidade: str, entidade_id: UUID, *, antes: Mapping[str, object] | None = None, depois: Mapping[str, object] | None = None, campos_pessoais: frozenset[str] = frozenset()) -> None`. A implementação aplica `mascarar` antes de gravar.
  - `aplicacao.consultar.ConsultarTrilha(repositorio).executar(contexto: ContextoConta, entidade: str, entidade_id: UUID) -> list[RegistroDeAcao]`: Admin e Operador; só registros com `conta_id == contexto.conta_id`; ordem crescente de `registrado_em`.
  - `adaptadores.registrador_sql.RegistradorSql(sessao: Session, relogio: Relogio)` (implementa a porta e `listar(conta_id, entidade, entidade_id) -> list[RegistroDeAcao]`).
  - `auditoria.api` reexporta `RegistradorDeAcoes`, `RegistroDeAcao`, `ConsultarTrilha`, `RegistradorSql`, `MARCADOR_PESSOAL`.
  - `tests/fakes/auditoria.RegistradorEmMemoria`: implementa a porta e guarda `registros: list[RegistroDeAcao]` (já mascarados).
  - Tabela `registro_acao` (migração `0002_auditoria`): `id PK BINARY(16)`, `conta_id BINARY(16) NULL`, `usuario_id BINARY(16) NULL`, `origem VARCHAR(20)`, `acao VARCHAR(80)`, `entidade VARCHAR(50)`, `entidade_id BINARY(16)`, `antes JSON NULL`, `depois JSON NULL`, `registrado_em DATETIME(6)`; índice `(conta_id, entidade, entidade_id, registrado_em)`. Grant `SELECT, INSERT` para `motoriz_app`. Gatilhos:

```sql
CREATE TRIGGER registro_acao_sem_update BEFORE UPDATE ON registro_acao FOR EACH ROW
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'registro_acao e imutavel';
CREATE TRIGGER registro_acao_sem_delete BEFORE DELETE ON registro_acao FOR EACH ROW
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'registro_acao e imutavel';
```

- [ ] **Step 1: Escrever os testes que falham**

```python
# tests/auditoria/test_registro.py
def test_mascarar_troca_so_campos_pessoais():
    dados = {"nome": "Ana", "email": "ana@x.com", "papel": "admin"}
    assert mascarar(dados, frozenset({"nome", "email"})) == {
        "nome": "[dado pessoal]", "email": "[dado pessoal]", "papel": "admin"}
    assert dados["nome"] == "Ana"

def test_mascarar_none():
    assert mascarar(None, frozenset({"nome"})) is None

# tests/auditoria/test_registrador_sql.py (banco)
def test_registra_e_consulta_mascarado(sessao, relogio_fixo):
    ator = Ator(conta_id=novo_id(), usuario_id=novo_id(), origem="usuario")
    alvo = novo_id()
    RegistradorSql(sessao, relogio_fixo).registrar(
        ator, "usuario.criado", "usuario", alvo,
        depois={"nome": "Ana", "papel": "operador"}, campos_pessoais=frozenset({"nome"}))
    [r] = RegistradorSql(sessao, relogio_fixo).listar(ator.conta_id, "usuario", alvo)
    assert r.depois == {"nome": "[dado pessoal]", "papel": "operador"}
    assert r.registrado_em == relogio_fixo.agora()

def test_consulta_nao_ve_outra_conta(sessao, relogio_fixo): ...
#  registra para conta A; ConsultarTrilha com contexto da conta B → []

# tests/auditoria/test_imutabilidade.py (banco)
@pytest.mark.parametrize("sql", [
    "UPDATE registro_acao SET acao = 'x'",
    "DELETE FROM registro_acao"])
def test_app_nao_altera_registro(motor_app, registro_gravado, sql):
    with motor_app.begin() as c, pytest.raises(DBAPIError):
        c.execute(text(sql))

@pytest.mark.parametrize("sql", [
    "UPDATE registro_acao SET acao = 'x'",
    "DELETE FROM registro_acao"])
def test_nem_migracao_altera_registro(motor_migracao, registro_gravado, sql):
    with motor_migracao.begin() as c, pytest.raises(DBAPIError, match="imutavel"):
        c.execute(text(sql))
```

`registro_gravado` grava um registro com id único pelo `motor_migracao`, faz commit e não limpa depois: a tabela é imutável por definição, e nenhum teste depende de ela estar vazia.

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/auditoria -v`
Expected: FAIL/ERROR.

- [ ] **Step 3: Implementar os arquivos listados e a migração `0002_auditoria.py`**

`registrado_em` sempre vem do `Relogio`, nunca do chamador.

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest -v; uv run lint-imports`
Expected: tudo passa.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(auditoria): trilha de ações imutável com mascaramento de dado pessoal"
```

---

### Task 7: Casos de uso de contas

**Files:**
- Create: `backend/src/motoriz/contas/aplicacao/sessao.py`, `usuarios.py`, `suporte.py`
- Create: `backend/src/motoriz/contas/api.py`
- Create: `backend/tests/fakes/contas.py`
- Test: `backend/tests/contas/aplicacao/test_sessao.py`, `test_usuarios.py`, `test_suporte.py`

**Interfaces:**
- Consumes: Tasks 3–6 (portas, entidades, `RegistradorDeAcoes`, `exigir_papel`, `Relogio`).
- Produces (todas as classes recebem as dependências no `__init__` por nome: `locadoras`, `usuarios`, `sessoes`, `hasher`, `relogio`, `auditoria`, só as que usam; o método é `executar`):
  - `sessao.SessaoEmitida` (frozen dataclass): `token: str`, `expira_em: datetime`.
  - `sessao.Entrar.executar(email: str, senha: str) -> SessaoEmitida`. Recusa a senha com mais de 128 caracteres antes de chamar o hasher. Levanta `CredenciaisInvalidas` em todos estes casos: e-mail inválido, usuário inexistente, senha errada, usuário inativo, locadora suspensa. Audita `"sessao.criada"` (entidade `"sessao"`).
  - `sessao.Sair.executar(token: str) -> None`: revoga, se a sessão existir e for válida; não falha se não existir. Audita `"sessao.encerrada"`.
  - `sessao.ResolverSessao.executar(token: str | None) -> ContextoConta`: levanta `SessaoInvalida` se o token faltar, se a sessão não existir, estiver revogada ou expirada, se o usuário estiver inativo ou se a locadora estiver suspensa.
  - `sessao.AlterarSenha.executar(contexto: ContextoConta, token_atual: str, senha_atual: str, senha_nova: str) -> None`: verifica a senha atual (`CredenciaisInvalidas` se errada), valida a nova, troca o hash, revoga as **outras** sessões do usuário (a de `token_atual` segue) e audita `"usuario.senha_alterada"` sem valores. `RepositorioSessoes.revogar_do_usuario` ganha o parâmetro opcional `exceto_hash: str | None = None`.
  - `usuarios.CriarUsuario.executar(contexto, nome: str, email: str, papel: Papel, senha_inicial: str) -> Usuario`: só Admin; `EmailJaCadastrado` se o e-mail já estiver em uso em qualquer conta; audita `"usuario.criado"` com `depois={"nome","email","papel","ativo"}` e `campos_pessoais={"nome","email"}`.
  - `usuarios.ListarUsuarios.executar(contexto) -> list[Usuario]`: só Admin.
  - `usuarios.DesativarUsuario.executar(contexto, usuario_id: UUID) -> None`: só Admin; `NaoEncontrado("Usuário não encontrado")` se o usuário não existir na conta; `verificar_pode_desativar`; revoga todas as sessões do usuário; audita `"usuario.desativado"` com `antes={"ativo": True}`, `depois={"ativo": False}`.
  - `usuarios.ReativarUsuario.executar(contexto, usuario_id: UUID) -> None`: só Admin; audita `"usuario.reativado"`.
  - `suporte.LocadoraCriada` (frozen dataclass): `locadora: Locadora`, `admin: Usuario`, `senha_inicial: str`.
  - `suporte.CriarLocadora.executar(nome, documento: str, contato, admin_nome, admin_email) -> LocadoraCriada`: `LocadoraJaCadastrada("Já existe uma locadora com este documento")` e `EmailJaCadastrado`; gera a senha inicial com `secrets.token_urlsafe(12)` (16 caracteres); audita `"locadora.criada"` e `"usuario.criado"` com `Ator(conta_id=<nova>, usuario_id=None, origem="suporte")`.
  - `suporte.SuspenderLocadora.executar(documento: str) -> None` e `suporte.ReativarLocadora.executar(documento: str) -> None`: `NaoEncontrado("Locadora não encontrada")`; auditam `"locadora.suspensa"`/`"locadora.reativada"` com origem `"suporte"`.
  - `contas.api` reexporta os casos de uso, `SessaoEmitida`, `LocadoraCriada` e os erros de `contas.dominio.erros`.
  - `tests/fakes/contas.py`: `LocadorasEmMemoria`, `UsuariosEmMemoria(conta_id: UUID | None)`, `SessoesEmMemoria`, `HasherFalso` (`gerar(s) = "hash:" + s`).

- [ ] **Step 1: Escrever os testes que falham**

```python
# tests/contas/aplicacao/test_sessao.py
def test_entrar_com_email_em_outra_caixa(cenario):
    emitida = cenario.entrar.executar(" ANA@Locadora.com ", "senha-segura-1")
    assert emitida.expira_em == cenario.relogio.agora() + timedelta(days=14)
    assert cenario.auditoria.registros[-1].acao == "sessao.criada"

@pytest.mark.parametrize("email,senha", [
    ("ana@locadora.com", "errada-errada"), ("ninguem@x.com", "senha-segura-1"), ("nao-e-email", "x" * 10)])
def test_entrar_falha_com_mesma_mensagem(cenario, email, senha):
    with pytest.raises(CredenciaisInvalidas, match="E-mail ou senha incorretos."):
        cenario.entrar.executar(email, senha)

def test_entrar_senha_gigante_nao_chama_hasher(cenario):
    with pytest.raises(CredenciaisInvalidas):
        cenario.entrar.executar("ana@locadora.com", "x" * 129)
    assert cenario.hasher.chamadas_verificar == 0

def test_entrar_bloqueado_para_locadora_suspensa(cenario):
    cenario.locadora.suspender()
    with pytest.raises(CredenciaisInvalidas):
        cenario.entrar.executar("ana@locadora.com", "senha-segura-1")

def test_resolver_sessao_de_usuario_desativado_falha(cenario):
    token = cenario.entrar.executar("ana@locadora.com", "senha-segura-1").token
    cenario.ana.desativar()
    with pytest.raises(SessaoInvalida):
        cenario.resolver.executar(token)

def test_resolver_sessao_de_locadora_suspensa_falha(cenario): ...
def test_resolver_sessao_expirada_falha(cenario):   # relogio.avancar(timedelta(days=14))
def test_resolver_sem_token_falha(cenario):         # executar(None)
def test_alterar_senha_revoga_outras_sessoes_e_mantem_atual(cenario): ...

# tests/contas/aplicacao/test_usuarios.py
def test_operador_nao_cria_usuario(cenario):
    with pytest.raises(AcessoNegado):
        cenario.criar.executar(cenario.ctx_operador, "Bia", "bia@x.com", Papel.OPERADOR, "senha-segura-1")

def test_email_duplicado_em_outra_conta(cenario): ...  # EmailJaCadastrado
def test_criar_usuario_audita_sem_dado_pessoal(cenario):
    u = cenario.criar.executar(cenario.ctx_admin, "Bia", "bia@x.com", Papel.OPERADOR, "senha-segura-1")
    r = cenario.auditoria.registros[-1]
    assert (r.acao, r.entidade_id) == ("usuario.criado", u.id)
    assert r.depois == {"nome": "[dado pessoal]", "email": "[dado pessoal]", "papel": "operador", "ativo": True}

def test_desativar_ultimo_admin_falha(cenario): ...
def test_desativar_revoga_sessoes(cenario): ...
def test_desativar_usuario_de_outra_conta_e_nao_encontrado(cenario): ...  # NaoEncontrado

# tests/contas/aplicacao/test_suporte.py
def test_criar_locadora_cria_admin_ativo(cenario_vazio):
    r = cenario_vazio.criar_locadora.executar("Loca Sul", "11.222.333/0001-81", "(51) 9999", "Ana", "ana@x.com")
    assert r.admin.papel is Papel.ADMIN and r.admin.ativo and len(r.senha_inicial) == 16
    assert [x.acao for x in cenario_vazio.auditoria.registros] == ["locadora.criada", "usuario.criado"]

def test_documento_duplicado(cenario_vazio): ...  # LocadoraJaCadastrada
def test_suspender_locadora_inexistente(cenario_vazio): ...  # NaoEncontrado
```

`cenario` e `cenario_vazio` são fixtures em `tests/contas/aplicacao/conftest.py`. O `cenario` monta uma locadora com a admin "Ana" (`ana@locadora.com`, senha `senha-segura-1`), um operador e uma segunda conta com um usuário, usando os fakes e um `RelogioFixo(2026-11-24T12:00Z)`. O `HasherFalso` conta as chamadas de `verificar`.

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/contas/aplicacao -v`
Expected: FAIL (imports).

- [ ] **Step 3: Implementar `sessao.py`, `usuarios.py`, `suporte.py`, `contas/api.py` e os fakes**

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest -v; uv run mypy src; uv run lint-imports`
Expected: tudo passa.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(contas): casos de uso de sessão, usuários e suporte"
```

---

### Task 8: API HTTP de contas e auditoria

**Files:**
- Create: `backend/src/motoriz/api/__init__.py`, `dependencias.py`, `erros.py`, `csrf.py`
- Create: `backend/src/motoriz/contas/adaptadores/rotas.py`, `esquemas.py`
- Create: `backend/src/motoriz/auditoria/adaptadores/rotas.py`
- Create: `backend/src/motoriz/exportar_openapi.py`
- Modify: `backend/src/motoriz/app.py`
- Test: `backend/tests/api/conftest.py`, `backend/tests/api/test_sessao.py`, `test_usuarios.py`, `test_csrf.py`, `test_trilha.py`

**Interfaces:**
- Consumes: Task 7 (casos de uso), Task 6 (`ConsultarTrilha`, `RegistradorSql`), Task 5 (repositórios SQL, `definir_conta`), Task 2 (`Configuracao`, `criar_fabrica`).
- Produces:
  - `criar_app(config: Configuracao | None = None) -> FastAPI`: guarda em `app.state` a fábrica de sessões, o relógio (`RelogioDoSistema`) e o hasher (`HasherArgon2`). Os testes substituem o relógio por `app.dependency_overrides[obter_relogio]`.
  - `api.dependencias`: `obter_sessao_banco(request) -> Iterator[Session]` (faz commit no fim e rollback em exceção); `obter_relogio(request) -> Relogio`; `obter_contexto(request, sessao) -> ContextoConta` (lê o cookie `motoriz_sessao`, chama `ResolverSessao` e depois `definir_conta`).
  - `api.erros.instalar_tratadores(app) -> None`: mapeamento da Global Constraints; `RequestValidationError` → 422 com `{"erro": "Dados inválidos", "campos": [...]}`.
  - `api.csrf.MiddlewareCsrf`: método fora de `GET/HEAD/OPTIONS` sem `X-Motoriz: 1` → 403 `{"erro": "Requisição não permitida"}`.
  - Rotas:
    - `POST /api/sessao` com `{email, senha}` → 204, grava o cookie (`max_age` 14 dias);
    - `GET /api/sessao` → 200 `{usuario_id, nome, email, papel, conta_id, conta_nome}`;
    - `DELETE /api/sessao` → 204, apaga o cookie;
    - `POST /api/sessao/senha` com `{senha_atual, senha_nova}` → 204;
    - `GET /api/usuarios` → 200 `[{id, nome, email, papel, ativo}]`;
    - `POST /api/usuarios` com `{nome, email, papel, senha_inicial}` → 201 `{id, nome, email, papel, ativo}`;
    - `POST /api/usuarios/{id}/desativar` e `POST /api/usuarios/{id}/reativar` → 204;
    - `GET /api/auditoria?entidade=&entidade_id=` → 200 `[{acao, origem, usuario_id, antes, depois, registrado_em}]`.
  - `python -m motoriz.exportar_openapi` imprime `criar_app().openapi()` em JSON no stdout, sem precisar de banco.
  - Fixtures em `tests/api/conftest.py`:
    - `cliente(motor_app)`: `TestClient` com a fábrica apontando para o container, `cookie_seguro=False` (o `TestClient` usa http, e um cookie `Secure` não voltaria) e o cabeçalho `X-Motoriz: 1` por padrão;
    - `cliente_2`: um segundo `TestClient` igual, com cookies separados (outro aparelho);
    - `cliente_sem_cabecalho`: igual ao `cliente`, mas sem `X-Motoriz`;
    - `conta_a` e `conta_b`: criadas com `CriarLocadora` em modo plataforma e com commit. Cada uma tem admin (senha trocada para `senha-segura-1`) e operador;
    - `entrar(cliente, email, senha)`: helper.
    - Os testes de API fazem commit de verdade. Para isolar um teste do outro, cada um usa e-mails e documentos únicos, gerados com `novo_id().hex`.

- [ ] **Step 1: Escrever os testes que falham**

```python
# tests/api/test_sessao.py  (banco)
def test_login_com_email_em_outra_caixa_grava_cookie(cliente, conta_a):
    r = cliente.post("/api/sessao", json={"email": f"  {conta_a.admin_email.upper()} ", "senha": "senha-segura-1"})
    assert r.status_code == 204
    cookie = r.headers["set-cookie"]
    assert "motoriz_sessao=" in cookie and "httponly" in cookie.lower() and "samesite=strict" in cookie.lower()
    assert cliente.get("/api/sessao").json()["papel"] == "admin"

def test_login_errado_401_mensagem_generica(cliente, conta_a):
    r = cliente.post("/api/sessao", json={"email": conta_a.admin_email, "senha": "errada-errada"})
    assert (r.status_code, r.json()) == (401, {"erro": "E-mail ou senha incorretos."})

def test_sem_cookie_401(cliente):
    assert cliente.get("/api/sessao").status_code == 401

def test_logout_invalida_cookie(cliente, conta_a): ...
def test_senha_nova_longa_demais_422(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, "senha-segura-1")
    r = cliente.post("/api/sessao/senha", json={"senha_atual": "senha-segura-1", "senha_nova": "x" * 129})
    assert r.status_code == 422

# tests/api/test_usuarios.py  (banco)
def test_admin_cria_e_lista(cliente, conta_a): ...
def test_operador_recebe_403(cliente, conta_a):
    entrar(cliente, conta_a.operador_email, "senha-segura-1")
    assert cliente.get("/api/usuarios").status_code == 403

def test_admin_nao_desativa_a_si_mesmo(cliente, conta_a):
    entrar(cliente, conta_a.admin_email, "senha-segura-1")
    r = cliente.post(f"/api/usuarios/{conta_a.admin_id}/desativar")
    assert (r.status_code, r.json()["erro"]) == (422, "Você não pode desativar o seu próprio usuário")

def test_usuario_desativado_perde_sessao_aberta(cliente, cliente_2, conta_a):
    entrar(cliente_2, conta_a.operador_email, "senha-segura-1")
    entrar(cliente, conta_a.admin_email, "senha-segura-1")
    cliente.post(f"/api/usuarios/{conta_a.operador_id}/desativar")
    assert cliente_2.get("/api/sessao").status_code == 401

def test_email_duplicado_409(cliente, conta_a, conta_b): ...

# tests/api/test_csrf.py
def test_post_sem_cabecalho_403(cliente_sem_cabecalho):
    r = cliente_sem_cabecalho.post("/api/sessao", json={"email": "a@b.com", "senha": "x" * 10})
    assert r.status_code == 403

# tests/api/test_trilha.py  (banco)
def test_trilha_do_usuario_criado(cliente, conta_a): ...
#  admin cria Bia; GET /api/auditoria?entidade=usuario&entidade_id=<id> → [ {acao: "usuario.criado", depois.nome: "[dado pessoal]"} ]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/api -v`
Expected: FAIL (rotas inexistentes; 404).

- [ ] **Step 3: Implementar dependências, erros, CSRF, rotas, esquemas e `exportar_openapi.py`; atualizar `criar_app`**

As rotas ficam finas: montam os repositórios SQL a partir da `Session` da requisição, chamam um caso de uso e convertem a resposta. Toda regra fica no caso de uso.

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest -v; uv run mypy src; uv run lint-imports; uv run python -m motoriz.exportar_openapi > /dev/null`
Expected: tudo passa; o export termina sem erro.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(api): sessão por cookie, gestão de usuários, trilha e proteção CSRF"
```

---

### Task 9: CLI de suporte

**Files:**
- Create: `backend/src/motoriz/contas/adaptadores/cli.py`
- Modify: `backend/pyproject.toml` (`[project.scripts] motoriz-suporte = "motoriz.contas.adaptadores.cli:main"`)
- Test: `backend/tests/contas/adaptadores/test_cli.py`

**Interfaces:**
- Consumes: Task 7 (`CriarLocadora`, `SuspenderLocadora`, `ReativarLocadora`), Task 5 (`modo_plataforma`).
- Produces: `main(argv: list[str] | None = None) -> int` (argparse) com os subcomandos:
  - `criar-locadora --nome --documento --contato --admin-nome --admin-email`: imprime `Locadora criada: <nome>\nAdmin: <email>\nSenha inicial: <senha>\nTroque a senha no primeiro acesso.`;
  - `suspender-locadora --documento` e `reativar-locadora --documento`.
  - Erro de domínio → imprime `Erro: <mensagem>` no stderr e devolve 1. Usa a `url_banco_app` da configuração, em sessão `modo_plataforma`, e faz commit.

- [ ] **Step 1: Escrever os testes que falham**

```python
# (banco) — monkeypatch MOTORIZ_URL_BANCO_APP para o container e limpar o cache de obter_configuracao
def test_criar_locadora_imprime_senha(capsys, banco_configurado):
    doc = cnpj_valido_unico()
    assert main(["criar-locadora", "--nome", "Loca Sul", "--documento", doc, "--contato", "x",
                 "--admin-nome", "Ana", "--admin-email", f"{novo_id().hex}@x.com"]) == 0
    assert "Senha inicial: " in capsys.readouterr().out

def test_documento_duplicado_sai_com_1(capsys, banco_configurado): ...

def test_suspender_derruba_sessao_aberta(cliente, conta_a, banco_configurado):
    entrar(cliente, conta_a.admin_email, "senha-segura-1")
    assert main(["suspender-locadora", "--documento", conta_a.documento]) == 0
    assert cliente.get("/api/sessao").status_code == 401
```

`cnpj_valido_unico()` é um helper em `tests/helpers.py` que gera um CNPJ com dígitos verificadores corretos a partir de 12 dígitos aleatórios. Ele também passa a ser usado pelas fixtures `conta_a` e `conta_b`.

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/contas/adaptadores/test_cli.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar `cli.py`**

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest -v`
Expected: tudo passa.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(contas): CLI de suporte para criar, suspender e reativar locadoras"
```

---

### Task 10: Suíte de isolamento entre contas

**Files:**
- Create: `backend/tests/isolamento/__init__.py`, `backend/tests/isolamento/casos.py`, `backend/tests/isolamento/test_isolamento.py`

**Interfaces:**
- Consumes: Task 8 (app, fixtures `cliente`, `conta_a`, `conta_b`, `entrar`).
- Produces (usado pelas fatias seguintes):
  - `casos.CasoDeIsolamento` (frozen dataclass): `metodo: str`, `caminho: str` (com placeholders como `{usuario_b}`), `corpo: dict | None`, `esperado: Literal["404", "lista_sem_dados_de_b"]`.
  - `casos.CASOS: dict[tuple[str, str], CasoDeIsolamento]`, cuja chave é `(método, caminho da rota no FastAPI)`.
  - `casos.ROTAS_SEM_CONTA: set[tuple[str, str]]`: `POST /api/sessao`, `GET /api/saude`, `GET /api/sessao`, `DELETE /api/sessao`, `POST /api/sessao/senha`, `GET /api/openapi.json`, `GET /api/docs`, `GET /api/docs/oauth2-redirect`. As de sessão só agem sobre o próprio usuário.
  - Cada fatia nova acrescenta seus casos em `CASOS`.

- [ ] **Step 1: Escrever os testes que falham**

```python
def test_toda_rota_tem_caso_de_isolamento(app):
    rotas = {(m, r.path) for r in app.routes if isinstance(r, APIRoute) for m in r.methods}
    faltando = rotas - set(CASOS) - ROTAS_SEM_CONTA
    assert not faltando, f"Rotas sem caso de isolamento: {sorted(faltando)}"

@pytest.mark.parametrize("chave", sorted(CASOS))
def test_conta_a_nao_alcanca_conta_b(cliente, conta_a, conta_b, chave):
    caso = CASOS[chave]
    entrar(cliente, conta_a.admin_email, "senha-segura-1")
    caminho = caso.caminho.format(usuario_b=conta_b.operador_id, admin_b=conta_b.admin_id)
    r = cliente.request(caso.metodo, caminho, json=caso.corpo)
    if caso.esperado == "404":
        assert r.status_code == 404 and str(conta_b.operador_id) not in r.text
    else:
        assert r.status_code == 200
        assert str(conta_b.admin_id) not in r.text and conta_b.admin_email not in r.text
```

Casos desta fatia:
- `GET /api/usuarios` → `lista_sem_dados_de_b`;
- `POST /api/usuarios/{id}/desativar` e `.../reativar` com `{usuario_b}` → `404`;
- `GET /api/auditoria?entidade=usuario&entidade_id={admin_b}` → `lista_sem_dados_de_b`;
- `POST /api/usuarios` com o e-mail de um admin da conta B → não se aplica, porque o e-mail é global e o 409 está coberto na Task 8. Colocar em `ROTAS_SEM_CONTA` com um comentário explicando o motivo.

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/isolamento -v`
Expected: `test_toda_rota_tem_caso_de_isolamento` FAIL até `casos.py` ficar completo. Os casos de 404 podem passar de primeira se as Tasks 5 e 7 estiverem corretas, e isso é o esperado. Para conferir que o teste pega o erro, retire temporariamente o filtro de conta em `instalar_filtro_de_conta` e veja os casos falharem. Depois restaure o filtro.

- [ ] **Step 3: Completar `casos.py`**

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest -v`
Expected: tudo passa.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "test: suíte de isolamento entre contas cobrindo todas as rotas"
```

---

### Task 11: Frontend — esqueleto PWA, login e usuários

**Files:**
- Create: `frontend/` (Vite `react-ts`), `frontend/vite.config.ts`, `frontend/src/main.tsx`, `src/App.tsx`
- Create: `frontend/src/api/cliente.ts`, `src/api/openapi.json` (gerado), `src/api/esquema.d.ts` (gerado)
- Create: `frontend/src/sessao/useSessao.ts`, `src/sessao/RotaProtegida.tsx`
- Create: `frontend/src/paginas/Entrar.tsx`, `src/paginas/Inicio.tsx`, `src/paginas/Usuarios.tsx`, `src/paginas/AlterarSenha.tsx`
- Test: `frontend/src/paginas/Entrar.test.tsx`, `Usuarios.test.tsx`, `frontend/src/testes/servidor.ts` (msw)

**Interfaces:**
- Consumes: as rotas HTTP da Task 8.
- Produces:
  - Script `npm run gerar:api`: `cd ../backend && uv run python -m motoriz.exportar_openapi > ../frontend/src/api/openapi.json && cd ../frontend && openapi-typescript src/api/openapi.json -o src/api/esquema.d.ts`.
  - `api/cliente.ts`: `export const api = createClient<paths>({ baseUrl: "", credentials: "include", headers: { "X-Motoriz": "1" } })`.
  - `sessao/useSessao.ts`: `useSessao(): { sessao: SessaoAtual | null; carregando: boolean; entrar(email: string, senha: string): Promise<void>; sair(): Promise<void> }`, em que `SessaoAtual` é o corpo de `GET /api/sessao`.
  - Rotas: `/entrar`, `/` (Início), `/usuarios` (só Admin), `/senha`. Sem sessão, `RotaProtegida` redireciona para `/entrar`.
  - `vite.config.ts`: `VitePWA({ registerType: "autoUpdate", manifest: { name: "Motoriz", short_name: "Motoriz", lang: "pt-BR", display: "standalone", theme_color: "#1f2937", icons: [...] } })`; proxy em dev `/api → http://localhost:8000`; ambiente `jsdom` no Vitest.
  - Textos fixos:
    - erro de login: `"E-mail ou senha incorretos."` (vem da API);
    - Operador acessando `/usuarios`: `"Apenas administradores podem gerenciar usuários."`;
    - botões `"Entrar"`, `"Sair"`, `"Novo usuário"`, `"Desativar"`, `"Reativar"`.
  - Layout pensado primeiro para o celular. A biblioteca de UI fica a critério do construtor (spec §7); nesta fatia basta CSS simples.

- [ ] **Step 1: Criar o projeto e gerar os tipos**

Run: `npm create vite@latest frontend -- --template react-ts`, instalar as dependências do Tech Stack e rodar `npm run gerar:api`.
Expected: `src/api/esquema.d.ts` contém `"/api/sessao"`.

- [ ] **Step 2: Escrever os testes que falham**

```tsx
// Entrar.test.tsx
test("mostra a mensagem da API quando o login falha", async () => {
  servidor.use(http.post("/api/sessao", () => HttpResponse.json({ erro: "E-mail ou senha incorretos." }, { status: 401 })));
  renderizarComRotas("/entrar");
  await userEvent.type(screen.getByLabelText("E-mail"), "ana@x.com");
  await userEvent.type(screen.getByLabelText("Senha"), "errada-errada");
  await userEvent.click(screen.getByRole("button", { name: "Entrar" }));
  expect(await screen.findByText("E-mail ou senha incorretos.")).toBeInTheDocument();
});

test("envia o cabeçalho X-Motoriz e vai para o início após o login", async () => { ... });

// Usuarios.test.tsx
test("operador vê aviso em vez da lista", async () => {
  sessaoComo("operador");
  renderizarComRotas("/usuarios");
  expect(await screen.findByText("Apenas administradores podem gerenciar usuários.")).toBeInTheDocument();
});

test("admin vê a lista e cria um usuário", async () => { ... });
test("erro da API ao desativar aparece na tela", async () => { ... });   // 422 "Você não pode desativar o seu próprio usuário"
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `npm test -- --run`
Expected: FAIL.

- [ ] **Step 4: Implementar o cliente, `useSessao`, `RotaProtegida` e as páginas**

- [ ] **Step 5: Rodar e ver passar; build**

Run: `npm test -- --run; npm run lint; npx tsc --noEmit; npm run build`
Expected: testes passam; build gera `dist/` com `manifest.webmanifest` e `sw.js`.

- [ ] **Step 6: Verificação manual ponta a ponta**

Com `docker compose up -d`, `uv run alembic upgrade head`, `uv run motoriz-suporte criar-locadora ...`, a API e `npm run dev` rodando: entrar com a senha inicial, trocá-la, criar um operador, entrar como ele numa janela anônima e confirmar que `/usuarios` mostra o aviso.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat(frontend): PWA com login, troca de senha e gestão de usuários"
```

---

### Task 12: Empacotamento e CI

**Files:**
- Create: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`
- Modify: `docker-compose.yml` (serviços `api` e `web`)
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`

**Interfaces:**
- Produces:
  - Serviço `api`: imagem Python 3.13 slim com `uv`; o comando roda `alembic upgrade head` com o usuário de migração e depois `fastapi run src/motoriz/app.py --port 8000`.
  - Serviço `web`: build do Vite servido por nginx na porta 8080, com proxy de `/api/` para `api:8000`.
  - CI com dois jobs no `ubuntu-latest`:
    - `backend`: `uv sync`, `ruff check`, `ruff format --check`, `mypy src`, `lint-imports`, `pytest` (testcontainers usa o Docker do runner);
    - `frontend`: Node 22, `npm ci`, `npm run lint`, `npx tsc --noEmit`, `npm test -- --run`, `npm run build`.

- [ ] **Step 1: Escrever os Dockerfiles, o `nginx.conf` e os serviços do compose**

- [ ] **Step 2: Verificar a subida completa**

Run: `docker compose up -d --build` e depois `curl http://localhost:8080/api/saude`
Expected: `{"status":"ok"}`.

- [ ] **Step 3: Escrever `.github/workflows/ci.yml` e atualizar o README (seção "Rodando tudo com Docker")**

- [ ] **Step 4: Verificar o CI localmente, na medida do possível**

Run: os mesmos comandos dos dois jobs, em `backend/` e `frontend/`.
Expected: todos passam.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "ci: imagens da api e do web, compose completo e workflow do GitHub Actions"
```
