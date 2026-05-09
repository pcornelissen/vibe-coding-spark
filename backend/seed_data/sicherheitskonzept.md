# Sicherheitskonzept DataHub

## Klassifizierung
DataHub verarbeitet interne Geschäftsdaten der Vertraulichkeitsstufe "Intern" und "Vertraulich". Personenbezogene Daten (DSGVO-relevant) werden pseudonymisiert gespeichert.

## Netzwerksicherheit

### Zonen-Modell
- **DMZ:** API-Gateway (Kong), WAF (ModSecurity)
- **Application Zone:** FastAPI-Services, GraphQL-Gateway, Airflow
- **Data Zone:** PostgreSQL, Kafka, Delta Lake (S3)
- **Management Zone:** Monitoring, Logging, CI/CD

Kommunikation zwischen Zonen nur über definierte Ports und Protokolle. Alle interne Kommunikation über mTLS.

## Zugriffssteuerung

### Rollen
| Rolle | Berechtigungen |
|-------|---------------|
| data-viewer | Lesen aller Datasets |
| data-analyst | Lesen + SQL-Queries ausführen |
| data-engineer | Lesen + Schreiben + Pipeline-Management |
| platform-admin | Vollzugriff inkl. Infrastruktur |

### Authentifizierung
- OAuth2 / OpenID Connect via Keycloak
- Service-to-Service: mTLS mit Client-Zertifikaten
- API-Keys nur für Legacy-Integrationen (werden bis Q4 2026 abgelöst)

## Datenschutz

### Pseudonymisierung
Personenbezogene Felder (Name, E-Mail, Telefon) werden im Bronze-Layer pseudonymisiert. Mapping-Tabelle liegt in separater, besonders geschützter Datenbank.

### Löschkonzept
- Löschanfragen über Self-Service-Portal
- Automatische Propagation in alle nachgelagerten Systeme innerhalb 72h
- Audit-Log über alle Löschvorgänge (Aufbewahrung: 3 Jahre)

## Schwachstellen-Management

Regelmäßige Penetrationstests (halbjährlich, externer Dienstleister). Container-Images werden bei jedem Build mit Trivy gescannt. CVEs mit CVSS ≥ 7.0 müssen innerhalb von 7 Tagen gepatcht werden.

## Abweichung zur Architektur-Dokumentation

Im Architekturüberblick wird die Verfügbarkeit mit 99.5% angegeben. Aus Sicherheitssicht empfehlen wir jedoch 99.9% für die API-Schicht, da Ausfälle zu Datenverlusten in nachgelagerten Systemen führen können. Dies ist noch nicht abschließend mit dem Product Owner abgestimmt.
