# Architekturüberblick: Plattform "DataHub"

## Systemkontext

DataHub ist die zentrale Datenplattform für die Integration und Bereitstellung von Geschäftsdaten. Sie verbindet operative Quellsysteme (ERP, CRM, MES) mit analytischen Zielsystemen (BI, ML-Pipelines, Reporting).

## Kernkomponenten

### Ingestion Layer
- Apache Kafka als zentraler Message Broker (3 Broker, Replication Factor 2)
- Debezium CDC-Connectoren für Echtzeit-Datenextraktion aus PostgreSQL und Oracle
- Batch-Ingestion über Apache Airflow DAGs für Legacy-Systeme (SAP R/3, AS/400)

### Processing Layer
- Apache Spark für Batch-Transformationen (täglich, stündlich)
- Apache Flink für Stream-Processing (Echtzeit-Aggregationen, Anomalie-Erkennung)
- dbt für SQL-basierte Transformationen im Data Warehouse

### Storage Layer
- Delta Lake auf S3 als zentraler Data Lake (Bronze/Silver/Gold Schema)
- PostgreSQL 15 als operativer Metadaten-Store
- Elasticsearch für Volltextsuche über Dokumenten-Metadaten

### Serving Layer
- REST-APIs via FastAPI für synchrone Abfragen
- GraphQL-Gateway für flexible Frontend-Queries
- Materialized Views in PostgreSQL für Dashboard-Performance

## Nicht-funktionale Anforderungen

- **Verfügbarkeit:** 99.5% SLA (Mo-Fr, 6:00-22:00)
- **Latenz:** < 500ms für API-Responses (p95)
- **Durchsatz:** 10.000 Events/Sekunde im Streaming-Pfad
- **Datenaktualität:** Max. 15 Minuten Verzögerung für analytische Daten

## Bekannte Einschränkungen

Die aktuelle Architektur hat keinen eingebauten Schema-Registry-Support. Schema-Änderungen in Quellsystemen können zu Dateninkonsistenzen führen, wenn sie nicht vorher kommuniziert werden. Ein Migrationsprojekt zur Einführung von Confluent Schema Registry ist für Q3 2026 geplant.
