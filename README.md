# Spark Docs

Webanwendung zur Konsolidierung technischer Dokumentation. Nutzer laden Dokumente verschiedener Formate in Projekte hoch, lassen sie über [SPARK](https://github.com/2Toad/spark) verarbeiten (Chunking, Embedding, Indexierung) und können dann:

- **Fragen stellen** — Chat-Interface gegen die indizierten Dokumente (RAG via Qdrant + LLM)
- **Zusammenfassungen erstellen** — Kernaussagen aller Dokumente zu einem Thema
- **Widersprüche finden** — Widersprüchliche Aussagen zwischen Dokumenten identifizieren
- **Konsolidieren** — Einheitliches Dokument aus mehreren Quellen ableiten

## Unterstützte Dokumentformate

PDF, Word (.docx), Markdown (.md), Plain Text (.txt), optional Excel (.xlsx)

## Architektur

```
Vue 3 SPA (PrimeVue)  ←→  FastAPI Backend  ←→  SPARK (DMS + Temporal)
                                  ↕                      ↕
                              PostgreSQL            Qdrant + LiteLLM
```

- **Frontend:** Vue 3, TypeScript, Vite, PrimeVue (Aura), Pinia, Vue Router
- **Backend:** Python 3.13, FastAPI, SQLAlchemy (async), Alembic, httpx, sse-starlette
- **Datenbank:** PostgreSQL (Port 15433, SPARK-Postgres, DB: `sparkdocs`)
- **Externe Services:** SPARK DMS (8002), LiteLLM (4000), Qdrant (6333), Temporal (8080)

## Voraussetzungen

- Python 3.13+ und [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- Laufende SPARK-Instanz (Docker Compose) mit PostgreSQL, Qdrant, LiteLLM, Temporal

## Setup

### Backend

```bash
cd backend
uv sync                                          # Dependencies installieren
uv run alembic upgrade head                       # DB-Migrationen ausführen
uv run uvicorn app.main:app --reload --port 8000  # Dev-Server starten
```

### Frontend

```bash
cd frontend
npm install          # Dependencies installieren
npm run dev          # Dev-Server starten (Port 5173)
```

### Datenbank anlegen

```bash
docker exec spark-workflow-postgres-1 psql -U postgres -c "CREATE DATABASE sparkdocs;"
```

Danach im Backend `uv run alembic upgrade head` ausführen.

## Nutzung

1. App öffnen: http://127.0.0.1:5173
2. Projekt anlegen
3. Dokumente hochladen (PDF, DOCX, MD, TXT)
4. "Verarbeitung starten" — SPARK-Workflow läuft (Chunking, Embedding, Indexierung)
5. Chat: Fragen an die Dokumente stellen
6. Konsolidierung: Zusammenfassung, Widerspruchsanalyse oder konsolidiertes Dokument erstellen

## Tests

```bash
cd backend && uv run pytest -v        # Backend-Tests (9 Tests, SQLite in-memory)
cd frontend && npm run type-check     # Frontend TypeScript-Prüfung
```

## Projektstruktur

```
backend/
  app/
    config.py          — Pydantic Settings (Env-Prefix: SPARK_DOCS_)
    models.py          — SQLAlchemy ORM (Project, Document, SparkWorkflow, ConsolidationResult)
    schemas.py         — Pydantic Request/Response Schemas
    database.py        — Async Engine + Session
    routers/           — API-Router (projects, documents, chat, workflows, consolidation)
    services/          — SPARK-Client, LLM-Client, Qdrant-Client, Prompt-Templates
  tests/               — pytest (async, SQLite in-memory)
  alembic/             — DB-Migrationen
frontend/
  src/
    views/             — ProjectList, ProjectDetail, ProjectChat, ProjectConsolidate
    stores/            — Pinia Stores
    api.ts             — API-Client mit SSE-Support
    types.ts           — Gemeinsame TypeScript-Typen
    router.ts          — Vue Router
```

## Umgebungsvariablen

Alle mit Prefix `SPARK_DOCS_` konfigurierbar:

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@127.0.0.1:15433/sparkdocs` | PostgreSQL-Verbindung |
| `SPARK_DMS_URL` | `http://127.0.0.1:8002` | SPARK DMS API |
| `LITELLM_URL` | `http://127.0.0.1:4000` | LiteLLM Proxy |
| `LITELLM_MODEL` | `gpt-oss-120b` | LLM-Modell |
| `QDRANT_URL` | `http://127.0.0.1:6333` | Qdrant Vektordatenbank |
| `QDRANT_COLLECTION` | `data_ollama` | Qdrant Collection |

## TODO
- UI testen
- Testdaten generieren
- Tests generieren
- Arc42-Dokumentation
- UI optimieren
- UI schöner machen
- Schauen, welches LLM-Modell wir wo nehmen können
- lokales Setup streamlinen für Devs in restriktiven Umgebungen
- wenn zentraleres Deployment möglich und gewünscht, User Auth?
- Verheiraten mit Dietmars Wunsch nach Arc-Tool?