# Logbuch – Vibe Coding Day: Spark Docs

## Tag 1 – 2026-05-08

### 14:00 – Brainstorming und Design

**Was wurde gemacht:**
Projektidee gemeinsam mit der KI erarbeitet: Eine Webanwendung zur Konsolidierung technischer Dokumentation über SPARK. Architektur (FastAPI + Vue 3 + PrimeVue), Datenmodell, API-Endpunkte und Frontend-Struktur entworfen. Arbeitsmodell für parallele Entwicklung mit Sync-Punkten definiert.

**Ergebnis:**
Design-Spec und Implementierungsplan stehen. 20 Tasks in 5 Phasen mit 4 Sync-Punkten. Die Aufteilung in Person A (Projekte + Dokumente) und Person B (Chat + Konsolidierung) ermöglicht paralleles Arbeiten.

**KI-Interaktion:**
- Ca. 8 Prompts für das gesamte Brainstorming (Formatfrage, Repo-Abgrenzung, Nutzer-Workflow, Tech-Stack, SPARK-Integration, Tagesziel, Arbeitsmodell, Sync-Punkte)
- Die KI hat die SPARK-Erfahrungsdatei und den bestehenden sparky-workspace selbstständig analysiert und daraus konkrete API-Patterns abgeleitet
- Musste einmal korrigiert werden: SQLite → PostgreSQL wegen parallelem Arbeiten, und Frontend-Aufteilung statt Backend/Frontend-Split
- Der strukturierte Brainstorming-Prozess (ein Frage pro Nachricht, Multiple-Choice) funktionierte gut

**Lernerkenntnis:**
Den Kontext früh und vollständig geben (Erfahrungsdokument, vorheriges Projekt) spart viele Rückfragen. Die KI musste bei Architekturentscheidungen korrigiert werden (SQLite→PostgreSQL, Feature-Split statt Layer-Split) — wichtige Constraints wie "zwei Personen arbeiten parallel" direkt am Anfang nennen, nicht erst wenn das Design schon steht. Der strukturierte Brainstorming-Ansatz (eine Frage pro Nachricht, Multiple-Choice) hat gut funktioniert, um die KI gezielt zu steuern.

### 14:57 – Backend Monorepo Setup (Task 1)

**Was wurde gemacht:**
Monorepo-Struktur mit Backend-Setup erstellt: `.gitignore` mit Python/Node-Patterns, `backend/pyproject.toml` mit FastAPI + SQLAlchemy + Pydantic + Testing-Dependencies (uv-PEP 723), `backend/app/` mit FastAPI-App und Config-Klasse (Pydantic Settings), `backend/tests/` mit conftest für AsyncClient-Fixture und Health-Check-Test.

**Ergebnis:**
✅ Alle 9 Dateien erstellt. `uv sync` erfolgreich (33 Packages installiert). Test `test_health` besteht (PASSED). Git-Commit erfolgreich.

**KI-Interaktion:**
- 1 Durchlauf: Task war präzise spezifiziert (exakte Dateipfade, exakte Code-Snippets)
- Keine Rückfragen, keine Anpassungen nötig
- Struktur war klar: Dateien schreiben → uv sync → Test laufen → Commit
- KI hat paralleles Erstellen (Write-Parallelisierung) nicht genutzt, sondern sequenziell erstellt (technisch unnötig, aber funktional okay)

**Lernerkenntnis:**
Sehr detaillierte Task-Specs (exakte Dateipfade, Code-Snippets) ermöglichen der KI einen fehlerfreien Durchlauf ohne Rückfragen. Die KI hat aber nicht von sich aus parallelisiert (mehrere unabhängige Dateien gleichzeitig schreiben), obwohl das möglich gewesen wäre — man muss Effizienz-Optimierungen explizit anweisen.

### 15:01 – Datenbankmodelle und Alembic-Migrationen (Task 2)

**Was wurde gemacht:**
`database.py` mit async SQLAlchemy Session-Factory erstellt, `models.py` mit vier Tabellen (Project, Document, SparkWorkflow, ConsolidationResult) inkl. Enums und Relationen. Alembic initialisiert, `alembic.ini` angepasst (leere sqlalchemy.url), `alembic/env.py` mit async-zu-sync URL-Konvertierung und direktem Import aus `app.models`. Zusätzlich `psycopg2-binary` als Dev-Dependency installiert für Alembic-Sync-Verbindungen.

**Ergebnis:**
✅ Alle Dateien korrekt erstellt. Alembic-Initialisierung erfolgreich. Autogenerate-Migration schlägt erwartungsgemäß fehl (PostgreSQL auf Port 15433 nicht erreichbar). Code ist korrekt und bereit für spätere DB-Verbindung. Git-Commit erfolgreich.

**KI-Interaktion:**
- 1 Durchlauf: Task war vollständig spezifiziert
- KI hat psycopg2-Fehler korrekt diagnostiziert und `psycopg2-binary` installiert
- DB-Verbindungsfehler klar identifiziert als erwartetes Verhalten (kein SPARK-Postgres aktiv)
- Sequenzielles Erstellen der Dateien, dann Alembic-Init, dann Migration-Versuch

**Lernerkenntnis:**
Die KI hat den psycopg2-Fehler selbstständig diagnostiziert und behoben, ohne dass eine Rückfrage nötig war. Zeigt: Wenn die Task-Spec vollständig ist, kann die KI auch unerwartete Probleme eigenständig lösen. Das erwartete Scheitern der Migration (kein Postgres aktiv) wurde korrekt als "nicht blockierend" eingeordnet — gutes Urteilsvermögen bei der Unterscheidung von echten Fehlern vs. erwartbarem Verhalten.
(Zeit war relativ lang, weil ich kurz nicht am Rechner war und claude auf Berechtigungen gearbeitet hat)