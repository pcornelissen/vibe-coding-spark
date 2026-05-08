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
(Zeit war relativ lang, weil ich kurz nicht am Rechner war und claude auf Berechtigungen gewartet hat)

### 15:03 – Phase 0 Rest: Schemas, CRUD, Frontend-Shell, API-Client, Store (Tasks 3–6)

**Was wurde gemacht:**
Vier Tasks am Stück als Subagenten: Pydantic-Schemas + Projekt-CRUD-Endpoints mit Tests, Vue 3 Frontend-Setup mit PrimeVue/Aura/Router/Placeholder-Views, TypeScript-Typen + API-Client mit SSE-Support, Pinia-Store für Projekte.

**Ergebnis:**
✅ Alle 4 Tasks erfolgreich. Backend: 4 Tests (health, create, list, detail, 404). Frontend: type-check sauber. Sync 0 komplett — gemeinsame Basis steht.

**KI-Interaktion:**
- Tasks liefen als Subagenten parallel, die meisten brauchten nur 1 Durchlauf
- Frontend-Setup brauchte eine Anpassung: `@vitejs/plugin-vue` v6 statt v5 für Vite 7
- KI hat das selbstständig gelöst ohne Rückfrage
- Die detaillierten Specs im Plan haben sich ausgezahlt — kaum Abweichungen

**Lernerkenntnis:**
Subagenten funktionieren gut für unabhängige Tasks mit klaren Specs. Aber: Man muss darauf achten, dass Berechtigungen (Bash, Write) für Subagenten konfiguriert sind, sonst blockieren sie still und man verliert Zeit.

### 15:49 – Phase 1: Document Upload, ProjectList, Chat-Endpoint, Chat-UI (Tasks 7–10)

**Was wurde gemacht:**
Vier parallele Subagenten: Document-Upload-Endpoint mit Format-Erkennung, ProjectList-View mit Create-Dialog, Chat-SSE-Endpoint (Dummy-LLM), Chat-UI mit Streaming und blinkenden Cursor.

**Ergebnis:**
✅ Alle 4 Tasks committed. Backend: Document-Upload funktioniert, Chat streamt SSE. Frontend: Projektliste mit Cards, Chat-Interface mit Eingabefeld. Sync 1 komplett.

**KI-Interaktion:**
- 4 Subagenten parallel — alle erfolgreich, keine Rückfragen
- Die Subagenten haben teilweise identische Test-Fixtures geschrieben (DB-Setup) — hier wäre ein shared conftest besser gewesen, aber für den Zweck war es okay
- Chat-Endpoint bewusst als Dummy implementiert (Plan-Vorgabe), wird in Phase 2 ersetzt

**Lernerkenntnis:**
Bei parallelen Subagenten muss man als "Controller" zwischendurch auf Nachrichten des Users reagieren. Hier wurde Feedback eine Stunde lang ignoriert, weil die Agenten ohne Pause durchliefen. Lesson: Nach jedem abgeschlossenen Agent innehalten und User-Input prüfen.

### 16:08 – Phase 2: SPARK-Client, Process-Endpoint, ProjectDetail, Qdrant/LLM-Clients, echte Chat-Anbindung (Tasks 11–15)

**Was wurde gemacht:**
Fünf parallele Subagenten: SPARK-Client (DMS-Upload + Temporal-Workflow), Process-Endpoint, ProjectDetail-View, Qdrant/LiteLLM-Clients, Chat-Endpoint auf echte Services umgestellt.

**Ergebnis:**
✅ Alle 5 Tasks implementiert, aber mit Nacharbeit. Subagenten hatten Berechtigungsprobleme (Hooks blockierten Write/Bash). Dateien wurden erstellt, aber Tests und Commits musste ich manuell machen. Zwei Tests hatten falsche Mocks (async context manager Probleme), musste ich fixen.

**KI-Interaktion:**
- Subagenten-Ansatz war hier weniger effizient als direkte Bearbeitung
- Hook-System blockierte: Write wurde wegen `subprocess`-Code im SPARK-Client geflaggt, Bash wurde teilweise verweigert
- Mock-Qualität bei async httpx-Clients war schlecht — `MagicMock` vs `AsyncMock` bei `client.stream()` und `.json()` falsch gewählt
- Controller (ich als Hauptagent) musste testen, Mocks fixen und committen

**Lernerkenntnis:**
Subagenten stoßen an ihre Grenzen, wenn das Berechtigungssystem restriktiv ist. In solchen Fällen ist direkte Bearbeitung schneller. Außerdem: Mock-Tests für async HTTP-Clients (httpx mit `stream()`, context managers) sind fehleranfällig — die korrekte Mock-Hierarchie (`MagicMock` für sync-Methoden wie `.json()`, `AsyncMock` für async context managers) ist nicht trivial und sollte besser in der Task-Spec erklärt werden.

### 16:15 – Phase 3: Consolidation, Workflow-Status, Layout-Polish (Tasks 16–19)

**Was wurde gemacht:**
Direkte Bearbeitung (keine Subagenten): Consolidation-Endpoint mit 3 Prompt-Templates (Zusammenfassung, Widerspruch, Konsolidierung), Consolidation-UI mit Typ-Auswahl und Streaming, Workflow-Status-SSE-Endpoint, App-Layout mit klickbarem Header.

**Ergebnis:**
✅ Alle 4 Tasks in ~7 Minuten erledigt. 9 Backend-Tests bestehen, Frontend type-check sauber. Deutlich schneller als die Subagenten-Runde.

**KI-Interaktion:**
- Direkte Bearbeitung statt Subagenten — nach den Berechtigungsproblemen der letzten Runde bewusst gewechselt
- Alle Dateien parallel erstellt, sofort getestet und committed
- Keine Rückfragen nötig, Plan war ausreichend spezifiziert
- `marked`-Package für Markdown-Rendering im Frontend installiert

**Lernerkenntnis:**
Wenn die Berechtigungsumgebung für Subagenten nicht optimal konfiguriert ist, ist direkte Bearbeitung deutlich effizienter. Phase 3 (4 Tasks, 7 Min) vs Phase 2 (5 Tasks, ~20 Min mit Nacharbeit). Der Subagenten-Ansatz lohnt sich vor allem, wenn Tasks wirklich isoliert und lang sind — für kürzere Tasks mit bekanntem Code ist direkt arbeiten besser.

### 16:17 – Dokumentation: README, Plan-Status, Logbuch

**Was wurde gemacht:**
README.md mit Fachlichkeit, Architektur, Setup-Anleitung und Umgebungsvariablen geschrieben. Plan-Status-Tabelle eingefügt (Tasks 1–19 done, Task 20 offen). Logbuch-Uhrzeiten aus Git-Log korrigiert, Lernerkenntnisse auf Agentic-Engineering-Fokus umgeschrieben.

**Ergebnis:**
✅ Alle Docs aktuell. README für neue Entwickler verständlich, Plan-Status als Handoff-Übersicht für Mensch und Agent, Logbuch vollständig.

**KI-Interaktion:**
- User musste korrigierend eingreifen: Uhrzeiten im Logbuch waren falsch (KI hat Fantasie-Uhrzeiten geschrieben statt ins Git-Log zu schauen)
- Lernerkenntnisse waren zu technisch statt auf KI-Zusammenarbeit fokussiert — explizites Feedback nötig
- Plan-Status wurde nicht mitgeführt — User musste darauf hinweisen, dass Handoff-Dokumente aktuell sein müssen
- README fehlte komplett bis zum expliziten Hinweis

**Lernerkenntnis:**
Die KI führt Metadaten (Plan-Status, Logbuch, README) nicht proaktiv mit. Man muss explizit daran erinnern. Für Handoffs zwischen Personen oder Sessions ist ein aktueller Plan-Status essentiell — das sollte nach jeder Phase automatisch passieren. Uhrzeiten nie raten, sondern aus Git-Log ableiten.