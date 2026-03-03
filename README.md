# Pokédex Platform

![Python](https://img.shields.io/badge/python-3.14.2-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![Postgres](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![CI](https://img.shields.io/github/actions/workflow/status/jpvilarinho/pokedex-platform/ci.yml)

---

Implementação full-stack do desafio técnico **“API Pokédex”** usando **FastAPI + PostgreSQL + React + Redux + Docker Compose**, integrando dados com a **PokeAPI**.

## Objetivo do projeto

Construir uma API Pokédex capaz de:

- consumir dados da PokeAPI
- persistir Pokémon em banco relacional
- listar Pokémon ordenados e paginados
- exibir detalhes no estilo Pokédex
- marcar Pokémon como capturado
- exportar lista em XML

---

## Clonar o repositório

```bash
git clone https://github.com/jpvilarinho/pokedex-platform.git
cd pokedex-platform
```

## Selecionar o interpretador Python correto (ambiente virtual)

Caso esteja rodando o backend localmente (sem Docker), utilize o interpretador do ambiente virtual criado no projeto:

```bash
.\.venv\Scripts\python.exe
```

No VS Code, por exemplo:

`Ctrl + Shift + P`

Digite: `Python: Select Interpreter`

Selecione:

```bash
Python 3.14.2 .\.venv\Scripts\python.exe
```

---

## Como rodar frontend local

```bash
cd frontend
npm install
npm run dev
```

---

## Backend (FastAPI)

- [x] Consumo da PokeAPI com **httpx (async)**
- [x] Concorrência via **asyncio.Semaphore**
- [x] Ordenação alfabética por nome
- [x] Paginação real com `offset` e `limit`
- [x] Persistência em **PostgreSQL** (SQLAlchemy async + asyncpg)
- [x] Cache DB-first: busca no banco antes de chamar PokeAPI
- [x] Enriquecimento Pokédex (species, evolution chain, weaknesses)
- [x] Exportação de lista ordenada para **XML**
- [x] Swagger/OpenAPI em `/docs`
- [x] Retry/backoff para chamadas externas (PokeAPI)
- [x] Testes com **pytest** + mock do PokeAPI (sem internet)
- [x] Dockerfile + migrations com Alembic

## Frontend (React + Redux)

- [x] Lista paginada com cards
- [x] Detalhe do Pokémon (estilo Pokédex)
- [x] Capturar/Soltar
- [x] Filtro “apenas capturados”
- [x] Exportar XML e baixar arquivo
- [x] Dockerfile

## CI/CD

- [x] GitHub Actions (`pytest` + `lint` + `build docker`)

---

## Arquitetura do repositório

```text
pokedex-platform
├── backend
│ ├── app
│ │ ├── api
│ │ ├── services
│ │ ├── models
│ │ ├── schemas
│ │ ├── crud
│ │ └── tests
│ ├── alembic
│ └── Dockerfile
├── frontend
│ ├── src
│ └── Dockerfile
└── docker-compose.yml
```

---

## Como rodar (Docker Compose)

Na raiz do projeto:

```bash
docker compose up --build
```

---

### Serviços

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- swagger: `http://localhost:8000/docs`

---

## Sincronizar dados (popular banco)

O banco inicia vazio. Para importar Pokémon da PokeAPI:

```bash
curl -X POST "http://localhost:8000/pokemon/sync?limit=200"
```

Para importar mais páginas:

```bash
curl -X POST "http://localhost:8000/pokemon/sync?offset=200&limit=200"
```

---

## Endpoints principais

Listagem (ordenada + paginada)

```json
- GET /pokemon
- GET /pokemon?offset=0&limit=20
- GET /pokemon?captured_only=true
- GET /pokemon?name=pika
```

Detalhes

```json
GET /pokemon/{id}
```

- Busca no DB primeiro
- Se não existir, busca na PokeAPI e persiste

```json
GET /pokemon/{id}/pokedex
```

- Enriquecimento (species + evolution + weaknesses)
- Persiste campos enriquecidos no DB

Capturar / Soltar

```json
- POST /pokemon/{id}/capture
- DELETE /pokemon/{id}/capture
```

Exportar XML

```json
GET /pokemon/export/xml
```

- Retorna `application/xml`
- Inclui header Content-Disposition para download do arquivo

---

## Testes

> Rode dentro do ambiente virtual (`.venv`).

### 1. Criar e ativar o ambiente virtual (Windows PowerShell)

```bash
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. Instalar dependências (inclui libs necessárias pros testes)

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio aiosqlite
```

### 3. Rodar os testes

```bash
python -m pytest -q
```

Os testes:

- não dependem de internet
- mockam a PokeAPI
- validam cache DB-first
- validam paginação e ordenação
- validam enrichment
- validam export XML

---

## Migrations (Alembic)

Se precisar rodar migrations manualmente:

```bash
cd backend
alembic upgrade head
```

---

## Build das imagens

```bash
docker build -t pokedex-backend ./backend
docker build -t pokedex-frontend ./frontend
```

---

## Concorrência e otimização

- Todas as operações de I/O externo são async (httpx.AsyncClient)
- Limite de concorrência com asyncio.Semaphore
- Retry/backoff exponencial para 429 e 5xx
- Estratégia DB-first para reduzir chamadas externas

---

## CI/CD (GitHub Actions)

O pipeline roda:

- `lint (ruff)`
- `pytest`
- build das imagens Docker (`backend + frontend`)

## Licença

MIT
