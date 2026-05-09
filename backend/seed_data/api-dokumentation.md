# API-Dokumentation DataHub

## Basis-URL
- Produktion: `https://api.datahub.internal/v2`
- Staging: `https://api.datahub-staging.internal/v2`

## Authentifizierung
Alle Requests erfordern einen Bearer-Token im Authorization-Header. Tokens werden über den internen OAuth2-Server ausgestellt (Keycloak).

```
Authorization: Bearer <token>
```

## Endpunkte

### GET /datasets
Listet alle verfügbaren Datasets auf.

**Query-Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| domain | string | Filter nach Fachdomäne (z.B. "finance", "logistics") |
| format | string | Ausgabeformat: "json" (default), "csv" |
| limit | int | Max. Ergebnisse (default: 50, max: 500) |

**Response:** 200 OK
```json
{
  "datasets": [
    {
      "id": "ds-001",
      "name": "Auftragsdaten",
      "domain": "logistics",
      "record_count": 1250000,
      "last_updated": "2026-05-08T14:30:00Z"
    }
  ],
  "total": 42
}
```

### GET /datasets/{id}/query
Führt eine SQL-Abfrage gegen ein Dataset aus.

**Query-Parameter:**
| Parameter | Typ | Beschreibung |
|-----------|-----|-------------|
| sql | string | SQL-Query (SELECT only) |
| timeout | int | Timeout in Sekunden (default: 30, max: 300) |

**Response:** 200 OK — Ergebnis als JSON-Array

### POST /datasets/{id}/export
Startet einen asynchronen Export.

**Request Body:**
```json
{
  "format": "parquet",
  "filter": "created_at > '2026-01-01'",
  "destination": "s3://exports/auftragsdaten-2026.parquet"
}
```

**Response:** 202 Accepted
```json
{
  "export_id": "exp-789",
  "status": "queued",
  "estimated_duration_seconds": 120
}
```

## Fehlerbehandlung

Alle Fehler folgen dem RFC 7807 Format:
```json
{
  "type": "https://datahub.internal/errors/rate-limited",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "Max 100 requests per minute. Retry after 23 seconds."
}
```

## Rate Limiting
- 100 Requests/Minute pro API-Key
- Bulk-Exports: max 5 gleichzeitig
- Query-Timeout: 300 Sekunden
