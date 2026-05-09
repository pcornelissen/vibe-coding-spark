# Vibe Coding Day

Wir führen einen Vibe Coding Day durch und wollen dabei die Erfahrungen dokumentieren.

## Dokumentation

Führe eine Datei `LOGBUCH.md` im Projektroot. Schreibe nach jedem größeren Schritt einen neuen Eintrag. Nutze dafür folgendes Format:

```markdown
### HH:MM – Kurztitel des Schritts

**Was wurde gemacht:**
Kurze Beschreibung (2–3 Sätze), was umgesetzt oder versucht wurde.

**Ergebnis:**
Hat es funktioniert? Wenn ja, wie gut? Wenn nein, woran lag es?

**KI-Interaktion:**
- Wie viele Anläufe/Prompts waren nötig?
- Musste der Kontext erklärt oder korrigiert werden?
- Hat die KI selbstständig sinnvolle Entscheidungen getroffen?
- Wurde Code generiert, der ohne Anpassung funktionierte?

**Lernerkenntnis:**
Was würdest du beim nächsten Mal anders machen?
```

Zusätzlich: Schreibe am Ende des Tages eine kurze **Zusammenfassung** (5–10 Sätze) ans Ende des Logbuchs mit einem Gesamtfazit zum Projekt und zur Arbeit mit der KI.

## Ziel

Wir wollen nachher zusammentragen:

1. Wie gut haben die anvisierten Projekte mit KI-Unterstützung funktioniert?
2. Wo waren KI-Agents besonders hilfreich, wo eher hinderlich?
3. Was haben wir als Menschen gut gemacht und wo sollten wir besser mit der KI interagieren?

## Hinweise für die Arbeit

- Beginne mit einem klaren, abgegrenzten Ziel für den Tag.
- Arbeite in kleinen Schritten und teste häufig.
- Wenn etwas nicht klappt, dokumentiere es und wechsle den Ansatz, statt zu lange an einem Problem festzuhalten.

## Projekt: Spark Docs

Eine Webanwendung zur Konsolidierung technischer Dokumentation über SPARK.

### Tech-Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy (async), Alembic, httpx, sse-starlette
- **Frontend:** Vue 3 (Composition API + TypeScript), Vite, PrimeVue, Pinia, Vue Router
- **Datenbank:** PostgreSQL (auf Port 15433, SPARK-Postgres)
- **Externe Services:** SPARK DMS (8002), LiteLLM (4000), Qdrant (6333), Ollama (11434), Temporal (8080)

### Projektstruktur

```
backend/          — FastAPI-Backend (uv als Package Manager)
  app/
    config.py     — Pydantic Settings, Env-Variablen mit Prefix SPARK_DOCS_
    models.py     — SQLAlchemy ORM-Models
    schemas.py    — Pydantic Request/Response-Schemas
    database.py   — Async Engine + Session
    routers/      — API-Router (projects, documents, chat, workflows, consolidation)
    services/     — SPARK-Client, LLM-Client, Qdrant-Client, Prompt-Templates
  tests/          — pytest (async, SQLite in-memory für Tests)
  alembic/        — Datenbankmigrationen
frontend/         — Vue 3 SPA
  src/
    views/        — ProjectList, ProjectDetail, ProjectChat, ProjectConsolidate
    stores/       — Pinia Stores
    api.ts        — API-Client mit SSE-Support
    types.ts      — Gemeinsame TypeScript-Typen
    router.ts     — Vue Router
```

### Befehle

```bash
# SPARK-Stack (Podman)
cd spark-workflow && podman compose up -d
cd spark-workflow && podman compose -f docker-compose.yaml -f docker-compose.services.yaml up -d --build dms-upload litellm-proxy extraction tika unoserver

# Datenbank
podman exec spark-workflow-postgresql-1 psql -U postgres -c "CREATE DATABASE sparkdocs;"

# Backend
cd backend && uv sync                              # Dependencies installieren
cd backend && uv run alembic upgrade head            # Migrationen ausführen
cd backend && uv run uvicorn app.main:app --reload  # Dev-Server starten (Port 8000)
cd backend && uv run pytest -v                      # Tests ausführen

# Frontend
cd frontend && npm install                          # Dependencies installieren
cd frontend && npm run dev                          # Dev-Server starten (Port 5173)
cd frontend && npm run type-check                   # TypeScript prüfen

# Testdaten (optional)
cd backend && uv run python seed_data/seed.py
```

### Arbeitsmodell

Zwei Personen arbeiten parallel an Feature-Branches mit regelmäßigen Sync-Punkten (max. 3h Abstand). Person A: Projekte + Dokumente. Person B: Chat + Konsolidierung. Spec und Plan liegen unter `docs/superpowers/`.

### SPARK-Integration

Die SPARK-API-Kommunikation folgt dem Muster aus dem vorherigen `sparky-workspace`:
1. DMS Upload: `generate-upload-url` → `PUT` auf Upload-URL → `confirm-upload`
2. Text/Markdown-Dateien werden zu PDF konvertiert (SPARK erwartet PDF/DOCX)
3. Temporal Workflow: Start via `docker exec` CLI mit `IsolatedFVPWorkflow`
4. Workflow-ID-Format: `sparky-{uuid}` (neue UUID pro Verarbeitung, nicht die DB-Projekt-ID)
5. Extraction: Tika statt Docling (kein ARM64-Image für docling-serve)

Dokumente werden lokal unter `backend/uploads/{project_id}/{doc_id}` gespeichert.

Referenz für lokale SPARK-Konfiguration: `spark-erfahrungen-und-loesungsansaetze.md`
