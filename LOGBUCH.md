# Logbuch – Vibe Coding Day: Spark Docs

## Tag 1 – 2026-05-08

### 10:30 – Brainstorming und Design

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
Den Kontext früh und vollständig geben (Erfahrungsdokument, vorheriges Projekt) spart viele Rückfragen. Wichtige Constraints (zwei Personen, paralleles Arbeiten) direkt am Anfang nennen, nicht erst wenn das Design schon steht.
