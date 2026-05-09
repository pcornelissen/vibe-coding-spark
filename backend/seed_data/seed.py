"""Seed-Script: Erstellt Testprojekte mit Dokumenten über die API."""

import httpx
import asyncio
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
SEED_DIR = Path(__file__).parent

PROJECTS = [
    {
        "name": "DataHub Plattform",
        "description": "Technische Dokumentation der zentralen Datenplattform DataHub — Architektur, Betrieb, API und Sicherheit.",
        "files": [
            "architektur-ueberblick.md",
            "betriebshandbuch.md",
            "api-dokumentation.md",
            "sicherheitskonzept.md",
            "onboarding-guide.txt",
        ],
    },
    {
        "name": "Leeres Testprojekt",
        "description": "Projekt ohne Dokumente — zum Testen der leeren Zustände in der UI.",
        "files": [],
    },
    {
        "name": "Einzeldokument-Projekt",
        "description": "Projekt mit nur einem Dokument, um den Minimalfall zu testen.",
        "files": [
            "architektur-ueberblick.md",
        ],
    },
]


async def seed():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        # Health-Check
        r = await client.get("/api/health")
        if r.status_code != 200:
            print(f"Backend nicht erreichbar: {r.status_code}")
            return

        for proj in PROJECTS:
            # Projekt anlegen
            r = await client.post("/api/projects", json={
                "name": proj["name"],
                "description": proj["description"],
            })
            if r.status_code != 201:
                print(f"Fehler beim Anlegen von '{proj['name']}': {r.status_code} {r.text}")
                continue

            project = r.json()
            project_id = project["id"]
            print(f"Projekt erstellt: {proj['name']} ({project_id})")

            # Dokumente hochladen
            for filename in proj["files"]:
                filepath = SEED_DIR / filename
                if not filepath.exists():
                    print(f"  Datei nicht gefunden: {filepath}")
                    continue

                with open(filepath, "rb") as f:
                    r = await client.post(
                        f"/api/projects/{project_id}/documents",
                        files={"file": (filename, f, "application/octet-stream")},
                    )

                if r.status_code == 201:
                    doc = r.json()
                    print(f"  Dokument hochgeladen: {filename} ({doc['id']})")
                else:
                    print(f"  Fehler bei {filename}: {r.status_code} {r.text}")

        # Zusammenfassung
        r = await client.get("/api/projects")
        projects = r.json()
        print(f"\n--- {len(projects)} Projekte in der Datenbank ---")
        for p in projects:
            print(f"  {p['name']}: {p.get('document_count', '?')} Dokumente")


if __name__ == "__main__":
    asyncio.run(seed())
