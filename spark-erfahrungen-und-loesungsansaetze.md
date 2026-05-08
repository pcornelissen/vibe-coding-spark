# SPARK: Erfahrungen und Lösungsansätze

Stand: 2026-05-08, ca. 10:05 Uhr

Dieses Dokument hält fest, was beim ersten lokalen SPARK-Versuch funktioniert hat und wo wir Zeit verloren haben. Es soll den nächsten Test beschleunigen. Es geht hier nicht um die fachliche Idee der App, sondern um SPARK selbst: Container, Temporal-Workflows, Inhaltsextraktion, LLM-Anbindung, Qdrant und typische Fehlbilder.

SPARK Repository: `https://gitlab.opencode.de/bmds/planungs-und-genehmigungsbeschleunigung/spark-workflow`

## Einordnung

Für unseren Zweck ist SPARK vor allem als Infrastruktur für dokumentenbasierte Prüf- und Analysepipelines nützlich. Dokumente landen im DMS, Temporal steuert die Verarbeitung, Inhaltsextraktion und LLM-Enrichment erzeugen strukturierte Zwischenergebnisse, Qdrant macht Inhalte such- und matchbar. Darauf kann man eine App setzen, in der ein Kunde oder ein Non-Profit ein Vorhaben, einen Gesetzesentwurf oder ein Regelwerk gegen vorhandene Anforderungen prüfen will.

Was SPARK allein nicht leisten sollte, ist eine belastbare fachliche oder rechtliche Entscheidung wie "dieses Vorhaben ist genehmigungsfähig" oder "dieser Entwurf ist rechtssicher". SPARK kann Dokumente einlesen, strukturieren, anreichern, durchsuchen und gegen andere Dokumente oder Anforderungen matchen. Für eine echte Entscheidung fehlen explizite Prüfregeln, nachvollziehbare Subsumtion, ein Umgang mit unvollständigen Informationen und klare Verantwortlichkeit. In unserem Test ist SPARK deshalb die Dokumenten- und Prüfinfrastruktur. Bewertungslogik, Risikoklassifikation und UI-Führung gehören in die App-Schicht oder in eigene Services.

## Kurzfazit

Der Ablauf App -> SPARK-DMS Upload -> Temporal Workflow Start -> Inhaltsextraktion -> LLM-Enrichment -> Qdrant läuft lokal.

Noch nicht stabil ist der komplette Root-Workflow bis zum Ende. Im letzten Lauf war `process-documents-workflow` erfolgreich abgeschlossen, Qdrant war ebenfalls durch, aber der Root wartete noch auf die finalen Matching-Workflows:

- `LLMMatchingWorkflow`
- `InhaltsverzeichnisMatchingWorkflow`

Als technischer Integrationstest reicht dieser Stand: Die Blocker rund um Docling, LiteLLM und Qdrant sind lokal umgangen oder gelöst.

## Lokale Repositories und relevante URLs

- App/Wrapper: `/Users/cornelissen/projects/test/sparky-workspace`
- SPARK-Clone: `/Users/cornelissen/projects/test/spark-workflow`
- SPARK Remote: `https://gitlab.opencode.de/bmds/planungs-und-genehmigungsbeschleunigung/spark-workflow`
- App UI: `http://127.0.0.1:5173`
- App Backend: `http://127.0.0.1:8000`
- SPARK Temporal UI: `http://127.0.0.1:8080`
- SPARK DMS Upload API für die App: `http://127.0.0.1:8002`
- LiteLLM Proxy: `http://127.0.0.1:4000`
- Apache Tika: `http://127.0.0.1:9998`
- Ollama auf dem Host: `http://127.0.0.1:11434`

## Wichtige lokale Änderungen im SPARK-Clone

Diese Änderungen liegen im SPARK-Clone und sind nicht upstream:

- `docker-compose.yaml`
  - Postgres Host-Port von `127.0.0.1:5432:5432` auf `127.0.0.1:15433:5432` geändert, weil lokal schon etwas auf 5432 lief.

- `docker-compose.services.yaml`
  - Interner `dms` Service nutzt `S3_EXTERNAL_URL: "http://minio:9000"`, damit Container beim Download nicht auf ihr eigenes `localhost:9000` zeigen.
  - `dms-upload` bleibt bei `S3_EXTERNAL_URL: "http://localhost:9000"`, weil die App vom Host aus hochlädt.
  - Neuer `tika` Service mit `apache/tika:latest`.
  - `extraction` bekommt `TIKA_URL: "http://tika:9998"`.
  - `extraction` nutzt für Ollama-Qdrant eine separate Collection:
    - `QDRANT_COLLECTION_NAME: "data_ollama"`
    - `QDRANT_DENSE_VECTOR_SIZE: "4096"`
  - LLM-Throttles wurden für den lokalen Ollama-Test auf `MAX_CONCURRENT: 1` reduziert.

- `04-shared-services/basiskomponenten/litellm-proxy/config.yaml`
  - `gpt-oss-120b` routet lokal auf `ollama/llama3`.
  - `mistral-small-24b-instruct` routet lokal auf `ollama/llama3`.
  - `BAAI/bge-m3` routet für Embeddings ebenfalls auf `ollama/llama3`.

- `05-modulcluster/modul-inhaltsextraktion/src/env.py`
  - `TIKA_URL` als Environment-Setting ergänzt.

- `05-modulcluster/modul-inhaltsextraktion/src/services/docling_processing/extraction.py`
  - Wenn `docling-serve` nicht erreichbar ist, fällt die Chunk-Extraction auf Tika zurück.
  - Verwendeter Tika-Endpunkt: `PUT /tika` mit `Accept: text/plain`.
  - Wichtig: `PUT /tika/text` mit `Accept: text/plain` führte bei Tika 3.3.0 lokal zu `406 Not Acceptable`.

## Docling-Problem und Tika-Lösung

Problem:

- `docling-serve` Image `ghcr.io/docling-project/docling-serve-cu128:latest` ist nur `linux/amd64`.
- Auf dem Mac/Podman war `docling-serve` nicht sinnvoll startbar.
- Das Image ist CUDA/NVIDIA-orientiert und für einen lokalen Apple-Silicon-Test unpraktisch.

Beobachtete Fehlbilder:

- `docling-serve` Container fehlt.
- Temporal Activity `download_and_prepare_pdf_docling` oder `extract_chunk_with_docling` schlägt fehl.
- Logbeispiele:
  - `All connection attempts failed`
  - `Name or service not known`
  - `docling-serve submit failed after 3 attempts`

Lösung:

- Apache Tika als leichten lokalen Fallback einsetzen.
- Image `apache/tika:latest` hat ein natives `arm64` Manifest und lief direkt.
- Test:

```bash
curl -sS http://127.0.0.1:9998/tika
```

Erwartung:

```text
This is Tika Server (Apache Tika 3.3.0). Please PUT
```

Funktionierender Plaintext-Test:

```bash
curl -T document.pdf -H "Accept: text/plain" http://127.0.0.1:9998/tika
```

## DMS/MinIO-Falle

Problem:

- Der interne `dms` Service erzeugte signierte Download-URLs mit `http://localhost:9000`.
- Aus Sicht des `extraction` Containers ist `localhost` aber der Container selbst, nicht MinIO.
- Dadurch scheiterte bereits `download_and_prepare_pdf_docling`.

Lösung:

- Nur für den internen `dms` Service:

```yaml
S3_EXTERNAL_URL: "http://minio:9000"
```

- Für `dms-upload` weiterhin:

```yaml
S3_EXTERNAL_URL: "http://localhost:9000"
```

Grund:

- Die App lädt vom Host aus hoch.
- Die SPARK-Worker laden containerintern herunter.

## LiteLLM und Ollama

Problem:

- SPARK war auf `gpt-oss-120b` konfiguriert.
- LiteLLM antwortete mit 500:

```text
litellm.InternalServerError: OpenAIException - Connection error.
Received Model Group=gpt-oss-120b
```

Lokaler Lösungsansatz:

- Ollama war auf dem Host vorhanden.
- Modell: `llama3:latest`
- LiteLLM Container erreicht Ollama über:

```text
http://host.docker.internal:11434
```

Direkter Test aus dem LiteLLM-Container:

```bash
docker exec -i spark-workflow-litellm-proxy-1 python - <<'PY'
import litellm
r = litellm.completion(
    model="ollama/llama3",
    api_base="http://host.docker.internal:11434",
    messages=[{"role": "user", "content": "Antworte nur mit OK."}],
    max_tokens=10,
    temperature=0,
)
print(r.choices[0].message.content)
PY
```

Proxy-Test nach Config-Änderung:

```bash
curl -sS http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer y9Y7BYhbm6IkUFX0pnqsIGD6e-pGN1NF9HxPzw8dc_Q" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss-120b","messages":[{"role":"user","content":"Antworte nur mit OK."}],"max_tokens":10,"temperature":0}' | jq .
```

Erwartung: `200 OK` und Inhalt `OK`.

Hinweis:

- Der erste Ollama-Aufruf kann länger dauern, weil das Modell geladen wird.
- Für den Test wurde LLM-Parallelität reduziert, sonst überfährt SPARK den lokalen Ollama-Prozess schnell.

## Embeddings und Qdrant

Problem:

- Nach erfolgreichem LLM-Enrichment scheiterte Qdrant mit:

```text
Server error '500 Internal Server Error' for url 'http://litellm-proxy:4000/v1/embeddings'
```

Ursache:

- `BAAI/bge-m3` war noch nicht lokal geroutet.
- Ollama `llama3` kann über LiteLLM Embeddings liefern, aber mit 4096 Dimensionen.
- Die bestehende Qdrant Collection `data` war auf 1024 Dimensionen angelegt.

Lösung für den Test:

- `BAAI/bge-m3` in LiteLLM ebenfalls auf `ollama/llama3` routen.
- Neue Collection `data_ollama` verwenden.
- `QDRANT_DENSE_VECTOR_SIZE=4096`.

Embedding-Test:

```bash
curl -sS http://127.0.0.1:4000/v1/embeddings \
  -H "Authorization: Bearer y9Y7BYhbm6IkUFX0pnqsIGD6e-pGN1NF9HxPzw8dc_Q" \
  -H "Content-Type: application/json" \
  -d '{"model":"BAAI/bge-m3","input":["test"]}' | jq '{model:.model, len:(.data[0].embedding|length), error:.error}'
```

Erwartung:

```json
{
  "model": "BAAI/bge-m3",
  "len": 4096,
  "error": null
}
```

## Letzter guter Lauf

Letzter relevanter Testlauf:

```text
WorkflowId: sparky-923c0912-4513-455b-87b4-627c370263f3
ProjectId: 923c0912-4513-455b-87b4-627c370263f3
```

Ergebnisse:

- Tika-Fallback wurde genutzt.
- `docling-extraction`: erfolgreich.
- Chat-LLM-Schritte mit Ollama: erfolgreich.
- `single-document-workflow`: erfolgreich für alle drei Dokumente.
- `build-qdrant-workflow`: erfolgreich.
- Log:

```text
Qdrant build complete: 3 succeeded, 0 failed.
```

Noch offen in diesem Lauf:

- Root `IsolatedFVPWorkflow` lief weiter.
- Pending:
  - `LLMMatchingWorkflow`
  - `InhaltsverzeichnisMatchingWorkflow`

## Nützliche Diagnosebefehle

SPARK Root-Workflows listen:

```bash
docker exec spark-workflow-temporal-admin-tools-1 temporal workflow list \
  --address temporal:7233 \
  --namespace default \
  --query 'WorkflowId STARTS_WITH "sparky-"' \
  --limit 20
```

Workflow beschreiben:

```bash
docker exec spark-workflow-temporal-admin-tools-1 temporal workflow describe \
  --address temporal:7233 \
  --namespace default \
  --workflow-id sparky-923c0912-4513-455b-87b4-627c370263f3
```

Zu einem Projekt gehörende Workflows:

```bash
docker exec spark-workflow-temporal-admin-tools-1 temporal workflow list \
  --address temporal:7233 \
  --namespace default \
  --query 'ProjectId = "923c0912-4513-455b-87b4-627c370263f3"' \
  --limit 30
```

Extraction-Logs filtern:

```bash
docker logs --since 20m spark-workflow-extraction-1 2>&1 | rg \
  'falling back to Tika|Workflow completed|Workflow failed|event.outcome":"failure|Qdrant build complete|litellm.InternalServerError'
```

LiteLLM Logs:

```bash
docker logs --tail 120 spark-workflow-litellm-proxy-1
```

Containerstatus:

```bash
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}' | rg 'spark-workflow-(tika|extraction|litellm|dms|temporal|qdrant|minio)'
```

## Empfohlener Start für den nächsten Versuch

1. Ollama starten und Modell prüfen:

```bash
ollama list
curl -sS http://127.0.0.1:11434/api/tags | jq .
```

2. SPARK Services starten:

```bash
cd /Users/cornelissen/projects/test/spark-workflow
docker compose -f docker-compose.yaml -f docker-compose.services.yaml up -d
```

Falls nur die geänderten Services neu gebaut werden sollen:

```bash
docker compose -f docker-compose.services.yaml up -d --build litellm-proxy extraction
docker compose -f docker-compose.services.yaml up -d tika dms dms-upload
```

3. Tika prüfen:

```bash
curl -sS http://127.0.0.1:9998/tika
```

4. LiteLLM Chat prüfen:

```bash
curl -sS http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer y9Y7BYhbm6IkUFX0pnqsIGD6e-pGN1NF9HxPzw8dc_Q" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss-120b","messages":[{"role":"user","content":"Antworte nur mit OK."}],"max_tokens":10}' | jq .
```

5. LiteLLM Embeddings prüfen:

```bash
curl -sS http://127.0.0.1:4000/v1/embeddings \
  -H "Authorization: Bearer y9Y7BYhbm6IkUFX0pnqsIGD6e-pGN1NF9HxPzw8dc_Q" \
  -H "Content-Type: application/json" \
  -d '{"model":"BAAI/bge-m3","input":["test"]}' | jq '{len:(.data[0].embedding|length), error:.error}'
```

6. Neuen App-Lauf starten und Temporal beobachten.

## Interpretation der Temporal UI

Nicht von vielen roten Workflows irritieren lassen.

- Alte fehlgeschlagene Workflows bleiben sichtbar.
- Child-Workflows können failed/terminated sein, obwohl ein späterer neuer Lauf weiterkommt.
- Für die Bewertung immer den neuesten `sparky-...` Root und dessen ProjectId heranziehen.

Wichtige Reihenfolge für die Diagnose:

1. `docling-extraction`
   - Wenn failed: Tika/Docling/DMS-MinIO prüfen.
2. `single-document-workflow`
   - Wenn failed: LLM-Enrichment oder Summarization prüfen.
3. `build-qdrant-workflow`
   - Wenn failed: Embeddings/Qdrant-Dimension/Collection prüfen.
4. `LLMMatchingWorkflow` und `InhaltsverzeichnisMatchingWorkflow`
   - Aktuell der nächste offene Bereich.

## Offene Punkte

- Das finale Matching ist noch offen.
- Die Qualität von `llama3` ist für diesen Zweck egal, aber die Laufzeit ist langsam.
- Für bessere Geschwindigkeit wäre ein kleineres Modell sinnvoll, zum Beispiel ein kleines Chat-Modell plus ein echtes kleines Embedding-Modell. Dann müsste die Qdrant-Dimension entsprechend gesetzt werden.
- Eine App um SPARK herum muss die gestarteten Läufe selbst monitoren: Root-Workflow und ProjectId merken, Child-Workflows auswerten, Completion erkennen und relevante Ergebnisse aus SPARK übernehmen.
