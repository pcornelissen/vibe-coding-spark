# Betriebshandbuch DataHub

## Deployment

### Voraussetzungen
- Kubernetes Cluster (mind. 3 Worker Nodes, je 16 vCPU, 64 GB RAM)
- Helm 3.12+
- kubectl Zugriff auf den Ziel-Cluster
- Vault-Token für Secret-Injection

### Deployment-Prozess
1. Helm Chart aus der internen Registry pullen: `helm pull oci://registry.internal/datahub`
2. Values-Datei für die Umgebung anpassen (`values-prod.yaml`)
3. `helm upgrade --install datahub ./datahub -f values-prod.yaml -n datahub`
4. Health-Checks prüfen: `kubectl get pods -n datahub`

### Rollback
Bei Fehlern: `helm rollback datahub <revision> -n datahub`

## Monitoring

### Dashboards
- **Grafana:** https://grafana.internal/d/datahub-overview
- **Kafka Monitoring:** https://grafana.internal/d/kafka-cluster
- **Airflow UI:** https://airflow.internal

### Alerting
Alerts werden über PagerDuty geroutet. Kritische Alerts:
- `datahub_ingestion_lag_high` — Kafka Consumer Lag > 100.000 Messages
- `datahub_api_error_rate_high` — API Error Rate > 5% über 5 Minuten
- `datahub_spark_job_failed` — Spark-Job fehlgeschlagen

### Log-Zugriff
Alle Logs werden nach Loki geschrieben. Query-Beispiel:
```
{namespace="datahub", container="api"} |= "ERROR"
```

## Wartungsfenster

Reguläre Wartung: Samstag 02:00–06:00 Uhr. Änderungen am Kafka-Cluster oder an der Datenbank nur in diesem Fenster. Ausnahmen erfordern Genehmigung durch den Platform Lead.

## Incident Response

1. Alert bestätigen in PagerDuty
2. Slack-Channel #datahub-incidents joinen
3. Runbook konsultieren (Confluence: "DataHub Runbooks")
4. Bei Datenverlust: Sofort Backup-Restore einleiten (siehe Abschnitt Backup)

## Backup & Recovery

- PostgreSQL: Automatisches Backup alle 6 Stunden via pgBackRest
- Delta Lake: Versioniert durch Delta-Log, Time Travel bis 30 Tage
- Kafka: Topic Retention 7 Tage, danach Archivierung nach S3
