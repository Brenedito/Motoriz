# Arquitetura do MVP do Motoriz

> Data: 24/11/2026 · Status: revisado, aguardando aprovação do autor · Base: `escopo_Motoriz.md` v0.2

## 1. Intenção

O Motoriz é um projeto de **portfólio**, construído por duas mãos (o autor e o Claude). O escopo funcional está fechado em `escopo_Motoriz.md`; este documento define **como** o MVP será construído.

O que o portfólio precisa mostrar: um domínio com regras de negócio reais (status de veículo, checklist imutável, comparação de vistoria, vencimento de manutenção, trilha de auditoria, LGPD), modelado com fronteiras claras, testado de verdade e com decisões registradas. A arquitetura deve ser defensável numa entrevista e, ao mesmo tempo, terminável por duas pessoas.

## 2. Objetivos, não objetivos e anti-objetivos

**Objetivos**
- Regras de negócio do escopo isoladas em código Python puro, testáveis sem banco nem HTTP.
- Fronteiras entre módulos explícitas e verificadas automaticamente.
- Checklist operável no celular, no pátio, sem perder dados quando a conexão cai (RF-19, seção 9 do escopo).
- Isolamento entre locadoras e trilha de auditoria imutável tratados como requisitos de primeira classe.
- Subir o sistema inteiro localmente com um comando.

**Não objetivos (v1)**
- Microsserviços, filas de mensagens, event sourcing.
- App nativo.
- Modo offline para o sistema todo (só checklist e km avulso; ver 6.6).
- Escala além do volume do escopo (até ~200 veículos por conta).

**Anti-objetivos (seria fracasso mesmo funcionando)**
- Uma locadora conseguir ver ou alterar dado de outra.
- Um checklist concluído ou um registro de auditoria poder ser alterado por qualquer caminho, inclusive SQL direto da aplicação.
- Uma foto de avaria tirada no pátio se perder por falta de conexão.
- Arquitetura cerimoniosa demais para duas pessoas terminarem.

## 3. Restrições

- **Backend:** Python + FastAPI (decisão do autor).
- **Frontend:** React (decisão do autor).
- **Banco:** um único MySQL compartilhado por todas as locadoras (decisão do autor).
- Volume, LGPD e retenção conforme seção 13 do escopo.
- Sem integrações externas na v1.
- **Sem prazo (decisão do autor):** o MVP inclui tudo o que o escopo marca como Essencial, inclusive os indicadores da seção 12 que não são "Desejável" (frota por status, taxa de ocupação, manutenções vencidas, histórico).

**Consequência do MySQL a registrar:** o MySQL não tem segurança por linha (row-level security) como o PostgreSQL. O isolamento entre locadoras não pode ser delegado ao banco e fica na aplicação, com uma rede de proteção automática e testes dedicados (ver 6.3). Também não há índice único parcial; onde ele seria necessário, usa-se coluna gerada (ver 6.4).

## 4. Abordagens consideradas

| # | Abordagem | Trade-off | Decisão |
|---|---|---|---|
| 1 | **Monólito modular com domínio isolado** (regras em Python puro, casos de uso, adaptadores para FastAPI/SQLAlchemy/armazenamento) | Regras testáveis sem infraestrutura e fronteiras visíveis; custa mais arquivos e mapeamento entre camadas | **Escolhida pelo autor** |
| 2 | FastAPI em camadas tradicionais (rotas → serviços → modelos ORM) | Mais rápido de escrever; regras acopladas ao banco, testes lentos, diferencia pouco no portfólio | Descartada |
| 3 | Event sourcing para locação e vistoria | Auditoria e imutabilidade nativas; pesado demais para dois construtores, consultas como "quem estava com o carro" ficam caras | Descartada |

## 5. Visão geral

```
 Celular / navegador (React PWA)
   │  IndexedDB: rascunhos de checklist, fotos, fila de envio
   │
   ├── HTTPS (JSON) ──────────────► API FastAPI (monólito modular)
   │                                   │
   └── PUT direto (URL assinada) ─►  Armazenamento de arquivos
                                       (MinIO local / S3 em produção)
                                       ▲
                                       │ verifica e calcula hash
                                   API ┘
                                       │
                                       ▼
                                     MySQL 8.4 (InnoDB, utf8mb4)
```

Um único processo de API. Não há worker em segundo plano na v1: alertas são calculados na leitura e o PDF é gerado na requisição (ver 6.9 e 6.10).

## 6. Decisões de arquitetura

### 6.1 Módulos

| Módulo | Responsabilidade (refs. do escopo) |
|---|---|
| `contas` | Locadora, usuários, papéis Admin/Operador, autenticação, sessão; área de Suporte Motoriz (RF-16, seção 4) |
| `frota` | Veículo, status, **histórico de mudanças de status** (base da taxa de ocupação, seção 12), leituras de km e regra "km nunca diminui" (F-01, F-08, RF-01, RF-02, RF-12, RN-08) |
| `clientes` | Cliente locatário PF/PJ, CNH, anonimização (RF-03, seção 13) |
| `locacao` | Locação, vínculos de veículo, troca, cancelamento, rascunho (F-02, F-05, F-10, RN-01..04, 12..15, 18, 19) |
| `vistoria` | Modelos de checklist, checklist, adendo, comparação saída × devolução, relatório PDF (F-03, RF-05..08, RF-18, RN-09..11) |
| `manutencao` | Planos, manutenções, inspeção técnica, cálculo de vencimento (F-04, F-06, F-07, RF-09..11, RN-05, RN-07) |
| `alertas` | Painel de alertas, só leitura sobre os demais módulos (RF-13, seção 11) |
| `consultas` | Linha do tempo do veículo, "quem estava com o carro" (F-09, RF-14, RF-15) |
| `auditoria` | Registro de ação imutável e sua consulta (RF-20, RN-17) |
| `arquivos` | Anexos e fotos: URL de envio, confirmação, hash, download controlado |

`alertas` e `consultas` são módulos de leitura: podem consultar tabelas de outros módulos diretamente via SQL de leitura, sem passar pelo domínio. Isso é intencional e fica documentado.

### 6.2 Estrutura interna de cada módulo

```
backend/src/motoriz/<modulo>/
  dominio/        entidades, objetos de valor, regras, erros — Python puro, sem FastAPI/SQLAlchemy
  aplicacao/      casos de uso (um por comando), portas (interfaces de repositório e serviços)
  adaptadores/    repositórios SQLAlchemy, rotas FastAPI, esquemas Pydantic
  api.py          fachada pública do módulo para os outros módulos
```

- **Regra de dependência:** `dominio` não importa nada de fora; `aplicacao` importa só `dominio`; `adaptadores` implementa as portas. Um módulo só importa outro pelo seu `api.py`. As duas regras são verificadas no CI com `import-linter`.
- **Mapeamento:** entidades de domínio são dataclasses; o SQLAlchemy usa modelos próprios nos adaptadores e o repositório converte. (Alternativa considerada: mapeamento imperativo do SQLAlchemy direto nas dataclasses — menos código, mas vaza detalhes de persistência para o domínio.)
- **Unidade de trabalho:** um caso de uso = uma transação. Quando um comando afeta vários módulos (ex.: concluir checklist de devolução → encerrar locação → mudar status do veículo), o caso de uso dono do fluxo chama as fachadas dos outros módulos dentro da mesma unidade de trabalho. Não há eventos assíncronos entre módulos na v1.
- **Dono de cada fluxo cruzado:** `locacao` orquestra F-02, F-05 e F-10; `manutencao` orquestra F-06 (e pede a `frota` a mudança de status); `frota` é a única que altera status e km do veículo.

### 6.3 Isolamento entre locadoras (multi-tenant)

- Toda tabela de dado de locadora tem `conta_id`. Chaves únicas de negócio incluem `conta_id` (ex.: `(conta_id, placa)`, `(conta_id, documento)`). Índices começam por `conta_id`.
- A conta vem **sempre** da sessão autenticada, nunca do corpo ou da URL.
- **Primeira linha:** repositórios recebem um `ContextoConta` e filtram por ele.
- **Rede de proteção:** um evento `do_orm_execute` do SQLAlchemy aplica `with_loader_criteria(conta_id == atual)` a todo modelo marcado como "da conta"; consulta sem contexto de conta levanta erro, exceto em código explicitamente marcado como de plataforma (Suporte).
- **Testes de isolamento:** uma suíte cria duas contas e tenta, por cada rota da API, ler e alterar dados da outra; toda tentativa deve falhar com 404.
- IDs são UUID gerados no cliente ou no servidor (UUIDv7, guardado como `BINARY(16)`), o que também evita enumeração.

### 6.4 Concorrência e invariantes no banco

- **Um veículo em uma locação ativa por vez (RN-12):** a tabela `vinculo_veiculo` tem uma coluna gerada `veiculo_vigente = IF(fim IS NULL, veiculo_id, NULL)` com índice único. Dois operadores tentando locar o mesmo carro: um vence, o outro recebe erro de "veículo não está mais disponível".
- Além disso, o caso de uso faz `SELECT ... FOR UPDATE` no veículo antes de mudar o status.
- Edições de cadastro (veículo, cliente) usam coluna `versao` para controle otimista.

### 6.5 Auditoria e imutabilidade

- **Registro de ação (RN-17):** tabela `registro_acao` (conta, usuário, data/hora do servidor, ação, entidade, id, valores anterior e novo em JSON). Cada caso de uso grava seus registros na **mesma transação** da mudança.
- **Sem dado pessoal na trilha:** para campos pessoais do cliente (nome, CPF/CNPJ, contato, endereço, CNH), o registro guarda só *qual* campo mudou, não os valores. Assim a anonimização (6.12) não esbarra na trilha imutável. *(Decisão do Claude; alternativa descartada: cifrar com chave por cliente e descartar a chave na anonimização — mais elegante, mais trabalho.)*
- Também se registra **leitura de dado pessoal sensível** (detalhe de cliente, download de foto de CNH, download de contrato), atendendo ao "registro de quem acessou" da seção 13.
- **Imutável no banco, não só na aplicação:**
  - o usuário MySQL da aplicação tem apenas `INSERT, SELECT` em `registro_acao`;
  - gatilhos `BEFORE UPDATE/DELETE` com `SIGNAL` bloqueiam alteração de `registro_acao` e de checklist (e seus itens e fotos) cujo estado seja concluído;
  - migrações rodam com outro usuário, com privilégios de DDL.
- **Adendo (RN-09):** registro novo ligado ao checklist, nunca alteração dele. Tem a mesma estrutura de avaria do checklist (peça, tipo, descrição, fotos obrigatórias) mais motivo. A comparação salva no encerramento **não** é recalculada; relatório e PDF mostram os adendos numa seção à parte, "registros posteriores". *(Decisão do Claude.)*
- **Correção de km (exceção da RN-08):** a leitura de km é entidade própria em `frota`. O Admin corrige criando uma leitura de origem "correção" que aponta para a leitura errada, com justificativa; a errada fica marcada como substituída, nunca apagada. O km atual do veículo passa a ser o da última leitura válida, e os vencimentos de manutenção são recalculados. Se a leitura errada veio de um checklist concluído, o checklist não muda e recebe um adendo automático citando a correção. *(Decisão do Claude.)*
- **Anexos nunca são sobrescritos:** substituir contrato cria um arquivo novo e mantém o anterior (seção 9).

### 6.6 Checklist no celular sem conexão

O frontend é uma PWA. O modo offline cobre **só** o preenchimento de checklist e o km avulso; o resto exige conexão.

- O rascunho do checklist e as fotos (como `Blob`) ficam no IndexedDB (via Dexie).
- O cliente gera os UUIDs do checklist, das avarias e das fotos. Todo comando enviado é **idempotente** pelo seu UUID: reenviar não duplica.
- **Fila de envio:** cada foto é enviada assim que houver conexão (pede URL assinada → `PUT` no armazenamento → confirma na API). O rascunho é sincronizado por `PUT /checklists/{id}` (substitui o rascunho inteiro).
- **Concluir exige conexão (decisão do autor).** O modo offline protege e retoma o preenchimento; ele não conclui nada. Concluir checklist, ativar locação (F-02), confirmar comparação e destino na devolução (F-05) e trocar veículo (F-10) são comandos online, síncronos, e só são aceitos quando todas as fotos exigidas já estão confirmadas no servidor. Sem conexão, o botão de concluir fica indisponível e a tela mostra o que falta ("aguardando envio de 7 fotos"). Conflitos como dois operadores locando o mesmo carro (6.4) aparecem na hora, para quem está no pátio. Contrato e demais anexos fora do checklist são enviados só online.
- **Hora:** a data/hora oficial da conclusão e da auditoria é a do servidor. A hora em que cada foto foi tirada no aparelho é guardada à parte como `capturada_em`.
- Fotos são redimensionadas no aparelho antes do envio (lado maior 1600 px, JPEG ~80%), para caber no volume da seção 13. *(Decisão do Claude; valor ajustável.)*
- Sessão expirada sem conexão: a fila espera o próximo login, sem descartar nada.

### 6.7 Arquivos e fotos

- Armazenamento compatível com S3: MinIO em desenvolvimento, S3 (ou similar) no deploy.
- Fluxo: API gera URL assinada de `PUT` com validade curta e chave `conta/<conta_id>/<arquivo_id>` → cliente envia → cliente confirma → API verifica tamanho e tipo, calcula **SHA-256** lendo o objeto e grava o metadado. O hash sustenta o valor probatório do checklist.
- Download sempre por URL assinada gerada pela API depois de checar conta e permissão (e auditar, se for dado pessoal).
- Bucket privado, sem acesso público.

### 6.8 Autenticação e permissões

- E-mail e senha próprios, hash **Argon2id**.
- **Sessão opaca** guardada no banco, enviada em cookie `HttpOnly; Secure; SameSite=Strict`. Desativar usuário invalida as sessões na hora. *(Escolhida no lugar de JWT por ser revogável e mais simples; decisão do Claude.)*
- Proteção CSRF: `SameSite=Strict` + exigência de um cabeçalho próprio em requisições que alteram dados.
- Permissões por papel (Admin, Operador) verificadas no **caso de uso**, não só na rota, conforme a tabela da seção 4 do escopo. Suporte Motoriz é um papel de plataforma separado, sem acesso a dados operacionais.

### 6.9 Alertas e vencimentos

- O vencimento de cada plano de manutenção (próximo km e próxima data) é calculado no domínio de `manutencao` e **persistido** sempre que muda a base: nova leitura de km, manutenção concluída, plano alterado. `frota` avisa `manutencao` pela fachada quando registra km.
- Os alertas (seção 11) são **calculados na leitura** comparando os valores persistidos com hoje e com o km atual. Com até ~200 veículos por conta isso é barato e dispensa agendador.

### 6.10 Comparação e relatório

- A comparação saída × devolução (RF-06, RN-11) é uma função pura do domínio de `vistoria`, que recebe dois checklists e devolve o relatório de diferenças. O resultado é gravado junto ao vínculo no encerramento (o relatório salvo não muda se o modelo de checklist mudar depois).
- O PDF (RF-18) é gerado na requisição a partir de um template HTML com **WeasyPrint**.

### 6.11 Modelos de checklist versionados

- Alterar um modelo cria uma nova versão; o checklist guarda referência à versão usada e uma cópia das peças e itens exigidos no momento em que foi criado (RF-08: alterar o modelo não altera checklists já feitos).

### 6.12 LGPD

- Caso de uso "anonimizar cliente" (Admin): substitui dados pessoais por marcadores, apaga a foto da CNH do armazenamento, mantém o histórico operacional. Cliente sem locação pode ser excluído.
- A anonimização automática após 5 anos (P8) **não** entra na v1, porque nenhum dado terá essa idade; o caso de uso existe e pode ser agendado depois.

## 7. Tecnologias

**Backend**
- Python 3.13, FastAPI, Pydantic v2.
- SQLAlchemy 2.0 **síncrono** com PyMySQL; o FastAPI roda as rotas síncronas em threadpool. *(Decisão do Claude: com esse volume, o modo assíncrono só adiciona complexidade aos testes e à unidade de trabalho.)*
- Alembic para migrações (inclusive gatilhos e permissões).
- `uv` para dependências; `ruff` para lint e formatação; `mypy` estrito; `import-linter` para fronteiras.
- Testes: `pytest`; domínio sem banco; integração com MySQL real via `testcontainers`; API com o `TestClient` do FastAPI.
- `boto3` para S3/MinIO; `argon2-cffi`; `weasyprint`.

**Frontend**
- React + TypeScript + Vite; `vite-plugin-pwa` (Workbox) para o service worker.
- React Router; TanStack Query para dados online; Dexie para IndexedDB.
- Tipos do cliente HTTP gerados do OpenAPI do FastAPI (`openapi-typescript`).
- Testes: Vitest + Testing Library; Playwright para fluxos ponta a ponta (incluindo checklist com a rede desligada).
- Biblioteca de UI: fica com o construtor (requisito: telas de checklist usáveis com uma mão no celular).

**Ambiente**
- `docker compose` com: api, web (build estático servido por nginx), mysql, minio.
- CI no GitHub Actions: lint, tipos, fronteiras, testes de backend e frontend.

## 8. Estrutura do repositório

```
backend/          pyproject.toml, src/motoriz/<modulos>, tests/, alembic/
frontend/         package.json, src/, tests/
docs/
  escopo/         escopo_Motoriz.md (movido para cá)
  adr/            uma ADR por decisão da seção 6
  superpowers/specs/
docker-compose.yml
README.md
```

As decisões da seção 6 viram ADRs curtas em `docs/adr/` durante o plano, porque o registro das decisões faz parte do portfólio.

## 9. Testes por camada

| Camada | O que cobre | Como |
|---|---|---|
| Domínio | Regras RN-xx, comparação, cálculo de vencimento, transições de status | Testes unitários puros, rápidos, um por regra |
| Aplicação | Casos de uso com permissão, auditoria e orquestração entre módulos | Repositórios em memória |
| Adaptadores | Repositórios, gatilhos de imutabilidade, coluna gerada de RN-12, isolamento por conta | MySQL real via testcontainers |
| API | Contratos HTTP, sessão, CSRF, suíte de isolamento entre contas | TestClient |
| Frontend | Componentes do checklist, fila offline | Vitest |
| Ponta a ponta | Locar → vistoriar → devolver; checklist sem rede | Playwright |

## 10. O que fica com o construtor

- Biblioteca de componentes de UI e identidade visual.
- Nomes exatos de tabelas, rotas e esquemas, seguindo identificadores em português sem acento.
- Ordem das fatias de implementação (sugestão: contas → frota → clientes → vistoria → locação → manutenção → consultas/alertas).
- Onde hospedar uma demo pública, se houver.
