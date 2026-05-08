# Spark Docs — Design Spec

Stand: 2026-05-08

## Überblick

Spark Docs ist eine Webanwendung zur Konsolidierung technischer Dokumentation. Nutzer laden Dokumente verschiedener Formate in Projekte hoch, lassen sie über SPARK verarbeiten und können dann Fragen stellen, Widersprüche erkennen und konsolidierte Ergebnisse ableiten.

## Architektur

```
┌─────────────────────────────────────────────┐
│              Vue 3 SPA (Vite)               │
│  Projekte │ Dokumente │ Chat │ Konsolidierung│
└──────────────────┬──────────────────────────┘
                   │ REST + SSE
┌──────────────────▼──────────────────────────┐
│            FastAPI Backend                   │
│  Projekte │ Upload │ Queries │ Konsolidierung│
│  BackgroundTasks │ SSE-Streams              │
└───┬──────────┬──────────┬───────────────────┘
    │          │          │
    ▼          ▼          ▼
 SPARK-API  Qdrant    LiteLLM
 (DMS+WF)  (direkt)  (direkt)
```

- **FastAPI-Backend** als dünner Orchestrator mit eigener Projektlogik
- **PostgreSQL** für Projektmetadaten, Dokumentstatus, Ergebnisse (SPARK-Postgres mitnutzen oder eigene Instanz)
- **SQLAlchemy + Alembic** für ORM und Migrations
- **SSE (Server-Sent Events)** für Live-Feedback bei Workflow-Status und LLM-Streaming
- **SPARK** bleibt Black Box für Ingestion/Verarbeitung; bei Bedarf direkter Zugriff auf Qdrant und LiteLLM

## Unterstützte Dokumentformate

- PDF
- Word (.docx)
- Markdown (.md)
- Plain Text (.txt)
- Optional: Excel (.xlsx)

## Datenmodell

### Project

| Feld        | Typ      | Beschreibung           |
|-------------|----------|------------------------|
| id          | UUID     | Primärschlüssel        |
| name        | string   | Projektname            |
| description | text     | Optional               |
| created_at  | datetime | Erstellungszeitpunkt   |
| updated_at  | datetime | Letzte Änderung        |

### Document

| Feld              | Typ    | Beschreibung                               |
|-------------------|--------|--------------------------------------------|
| id                | UUID   | Primärschlüssel                            |
| project_id        | FK     | → Project                                  |
| filename          | string | Originaldateiname                          |
| format            | enum   | pdf, docx, md, txt, xlsx                   |
| upload_status     | enum   | pending, uploaded, processing, ready, failed |
| spark_document_id | string | Optional, von SPARK zurück                 |
| created_at        | datetime | Erstellungszeitpunkt                     |
| updated_at        | datetime | Letzte Änderung                          |

### SparkWorkflow

| Feld              | Typ      | Beschreibung                       |
|-------------------|----------|------------------------------------|
| id                | UUID     | Primärschlüssel                    |
| project_id        | FK       | → Project                          |
| spark_workflow_id | string   | z.B. "sparky-..."                  |
| spark_project_id  | string   | SPARK ProjectId                    |
| status            | enum     | running, completed, failed         |
| started_at        | datetime | Start                              |
| completed_at      | datetime | Optional, bei Abschluss            |

### ConsolidationResult

| Feld             | Typ      | Beschreibung                                  |
|------------------|----------|-----------------------------------------------|
| id               | UUID     | Primärschlüssel                               |
| project_id       | FK       | → Project                                     |
| query            | text     | Nutzerfrage oder Aufgabenstellung             |
| result_type      | enum     | consolidation, contradiction, summary         |
| result_content   | text     | LLM-Ergebnis als Markdown                     |
| source_documents | JSON     | Liste referenzierter Document-IDs             |
| created_at       | datetime | Erstellungszeitpunkt                          |

## API-Endpunkte

### Projekte

- `GET /api/projects` — Liste aller Projekte
- `POST /api/projects` — Projekt anlegen
- `GET /api/projects/{id}` — Projektdetails inkl. Dokumentstatus-Übersicht

### Dokumente

- `POST /api/projects/{id}/documents` — Datei(en) hochladen → an SPARK DMS weiterleiten
- `GET /api/projects/{id}/documents` — Dokumentliste mit Status
- `GET /api/documents/{id}` — Dokumentdetails inkl. Extraktionsergebnis

### SPARK-Workflows

- `POST /api/projects/{id}/process` — SPARK-Workflow starten
- `GET /api/projects/{id}/workflow-status` — SSE-Stream mit Live-Status

### Queries & Konsolidierung

- `POST /api/projects/{id}/chat` — Frage an die Dokumente → SSE-Stream
- `POST /api/projects/{id}/consolidate` — Konsolidierung anstoßen → SSE-Stream
- `GET /api/projects/{id}/results` — Gespeicherte Konsolidierungsergebnisse

### Konventionen

- SSE-Endpoints liefern `text/event-stream`
- Reguläre Endpoints liefern JSON
- Fehler einheitlich als `{detail: string}` mit HTTP-Status

## Frontend

### Tech-Stack

- Vue 3 + Composition API + TypeScript
- Vite als Build-Tool
- Vue Router
- Pinia für State Management
- PrimeVue als UI-Bibliothek

### Routen

| Pfad                        | View                                       |
|-----------------------------|---------------------------------------------|
| `/`                         | Projektliste (Dashboard)                    |
| `/projects/:id`             | Projektübersicht: Dokumente, Status, Aktionen |
| `/projects/:id/chat`        | Chat-Interface gegen Projektdokumente       |
| `/projects/:id/consolidate` | Konsolidierungs-View                        |

### Zentrale Komponenten

- **AppLayout** — Sidebar mit Projektnavigation, Hauptbereich
- **ProjectCard** — Projektkarte im Dashboard mit Kurzstatus
- **DocumentList** — Tabelle mit Status-Badges und Upload-Button
- **DocumentUpload** — Drag & Drop, Mehrfach-Upload
- **WorkflowStatus** — Live-Statusanzeige via SSE
- **ChatPanel** — Eingabe + Nachrichtenverlauf, LLM-Streaming via SSE
- **ConsolidationView** — Typ wählen, starten, Ergebnis als Markdown mit Quellenreferenzen

## SPARK-Integration

- **Upload:** `POST` an SPARK DMS-Upload API (Port 8002)
- **Workflow-Start:** SPARK-API → `spark_workflow_id` und `spark_project_id` lokal speichern
- **Status-Monitoring:** BackgroundTask pollt SPARK, Updates via SSE ans Frontend

## Konsolidierungslogik

Ablauf:

1. Nutzer wählt Konsolidierungstyp und gibt ggf. eine Frage ein
2. Backend holt relevante Chunks aus Qdrant (Semantic Search über alle Projektdokumente)
3. Chunks + Aufgabenstellung → LLM-Prompt via LiteLLM
4. LLM-Antwort streamt via SSE ans Frontend, wird als ConsolidationResult gespeichert

### Konsolidierungstypen

1. **Zusammenfassung** — Kernaussagen aller Dokumente zu einem Thema zusammenfassen
2. **Widerspruchserkennung** — Widersprüchliche Aussagen zwischen Dokumenten finden
3. **Anforderungsabgleich** — Prüfen ob Anforderungen aus Dokument A in Dokument B adressiert werden

### Prompt-Strategie

- Eigenes Prompt-Template pro Konsolidierungstyp
- Qdrant-Ergebnisse als Kontext inklusive Quellenangabe (Dokument + Abschnitt)
- LLM wird angewiesen, Quellenreferenzen in der Antwort mitzuführen

## Arbeitsmodell: Parallele Entwicklung

### Feature-basierte Aufteilung

| Person A: Projekte + Dokumente       | Person B: Chat + Konsolidierung         |
|---------------------------------------|-----------------------------------------|
| Backend: Projekt-CRUD, Upload,        | Backend: Qdrant-Queries, LLM-Calls,    |
| SPARK-Workflow-Start, Status-Monitoring | SSE-Streaming, Widerspruchserkennung  |
| Frontend: Projektliste, Dokument-     | Frontend: Chat-UI, Konsolidierungs-     |
| übersicht, Upload, Status             | View, Ergebnis-Darstellung              |

### Phasen mit Sync-Punkten

**Phase 0 — Gemeinsame Basis (~1–2h, zusammen)**
Monorepo-Setup, DB-Schema, SPARK-Client-Stub, Vue-Shell mit Router.
→ Sync 0: Push auf `main`, beide auf gleichem Stand.

**Phase 1 — Grundgerüst (~2–3h, parallel)**
A: Projekt-CRUD API + Projektliste. B: Chat-Endpoint (Dummy-LLM) + Chat-UI Shell.
→ Sync 1: Merge, gemeinsam testen, Layout-Konsistenz prüfen.

**Phase 2 — SPARK-Anbindung + echte Daten (~2–3h, parallel)**
A: Upload → SPARK-DMS, Workflow-Start, Status-Polling. B: Qdrant-Query, echte LLM-Antworten.
→ Sync 2: Merge, End-to-End: Dokument hochladen → verarbeiten → abfragen.

**Phase 3 — Konsolidierung + Polish (~2–3h, parallel)**
A: Dokumentendetailansicht, Extraktionsergebnisse. B: Widerspruchserkennung, Konsolidierungs-View.
→ Sync 3: Merge, Gesamttest.

**Phase 4 — Feinschliff + Demo (~1h, zusammen)**
Edge Cases, UX-Polish, Demo vorbereiten.
→ Final: Push, Logbuch-Zusammenfassung.

### Sync-Regeln

- Feature-Branches, Merge in `main` beim Sync
- Sync = beide ziehen, App gemeinsam starten und testen
- Konflikte sofort klären, nicht weiterbauen
- Maximale Zeit zwischen Syncs: ~3h

### Geteilte Basis (Phase 0)

- Monorepo-Struktur: `/backend`, `/frontend`
- DB-Models + Migrations
- SPARK-Client-Klasse (Basis)
- Vue-App mit Router + Layout-Shell
- Gemeinsame TypeScript-Typen

## Externe Abhängigkeiten

| Service       | URL (lokal)                | Zweck                        |
|---------------|----------------------------|------------------------------|
| SPARK DMS     | http://127.0.0.1:8002      | Dokument-Upload              |
| SPARK Temporal| http://127.0.0.1:8080      | Workflow-Monitoring (UI)     |
| LiteLLM       | http://127.0.0.1:4000      | LLM-Aufrufe + Embeddings    |
| Qdrant        | http://127.0.0.1:6333      | Vektor-Suche                 |
| Ollama        | http://127.0.0.1:11434     | LLM-Backend (hinter LiteLLM)|
