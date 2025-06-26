# 🛠️ k8s-reporter Configuration Guide

This guide provides comprehensive configuration instructions for k8s-reporter, covering all aspects from basic setup to advanced enterprise deployment scenarios.

## Table of Contents

- [Configuration File Overview](#configuration-file-overview)
- [Server Configuration](#server-configuration)
- [Authentication & Security](#authentication--security)
- [Resource Monitoring](#resource-monitoring)
- [Alerting System](#alerting-system)
- [Report Generation](#report-generation)
- [Dashboard Customization](#dashboard-customization)
- [External Integrations](#external-integrations)
- [Performance Tuning](#performance-tuning)
- [Environment Variables](#environment-variables)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Configuration File Overview

k8s-reporter uses YAML configuration files to define its behavior. The configuration is divided into logical sections:

- **server**: HTTP server and network settings
- **authentication**: User access and security
- **monitoring**: Resource polling and data collection
- **dashboard**: UI customization and layout
- **alerting**: Alert rules and notification channels
- **reporting**: Report generation and storage
- **integrations**: External service connections
- **performance**: Resource usage and optimization
- **logging**: Log configuration and output

### Default Configuration File

```yaml
# k8s-reporter configuration
apiVersion: reporter.k8s.io/v1
kind: ReporterConfig
metadata:
  name: default-config
  version: "1.0"

server:
  host: "0.0.0.0"
  port: 8080
  tls:
    enabled: false
    cert_file: ""
    key_file: ""
  cors:
    enabled: true
    allowed_origins: ["*"]
  rate_limiting:
    enabled: true
    requests_per_minute: 60

authentication:
  enabled: true
  type: "basic"  # basic, oauth2, ldap, oidc
  session_timeout: "24h"
  users:
    - username: "admin"
      password: "$2a$10$..."  # bcrypt hash
      roles: ["admin"]
    - username: "viewer"
      password: "$2a$10$..."
      roles: ["read-only"]

monitoring:
  kubernetes:
    kubeconfig_path: "~/.kube/config"
    context: ""  # empty means current context
    namespaces: []  # empty means all namespaces
    resource_types:
      - pods
      - services
      - deployments
      - configmaps
      - secrets
      - persistentvolumes
      - persistentvolumeclaims
  refresh_interval: "30s"
  batch_size: 100
  timeout: "10s"
  include_events: true
  include_metrics: true

dashboard:
  title: "Kubernetes Cluster Dashboard"
  theme: "light"  # light, dark, auto
  auto_refresh: true
  refresh_interval: "10s"
  default_namespace: "default"
  widgets:
    - type: "cluster_overview"
      enabled: true
      position: {row: 1, col: 1, width: 12, height: 4}
    - type: "namespace_summary"
      enabled: true
      position: {row: 5, col: 1, width: 6, height: 6}
    - type: "resource_health"
      enabled: true
      position: {row: 5, col: 7, width: 6, height: 6}

alerting:
  enabled: true
  evaluation_interval: "1m"
  rules:
    - name: "pod_failures"
      condition: "pod_status == 'Failed'"
      severity: "critical"
      threshold: 1
      duration: "5m"
    - name: "high_resource_usage"
      condition: "cpu_usage > 80 OR memory_usage > 85"
      severity: "warning"
      threshold: 3
      duration: "10m"
  channels:
    - type: "email"
      name: "ops-team"
      config:
        to: ["ops@company.com"]
        smtp_server: "smtp.company.com:587"
        username: "alerts@company.com"
        password: "${SMTP_PASSWORD}"
    - type: "slack"
      name: "ops-slack"
      config:
        webhook_url: "${SLACK_WEBHOOK_URL}"
        channel: "#k8s-alerts"
    - type: "webhook"
      name: "custom-webhook"
      config:
        url: "https://api.company.com/alerts"
        headers:
          Authorization: "Bearer ${API_TOKEN}"

reporting:
  enabled: true
  schedule: "0 6 * * *"  # Daily at 6 AM
  formats: ["html", "pdf", "json"]
  output_directory: "./reports"
  retention:
    days: 30
    max_size_gb: 5
  templates:
    - name: "daily_summary"
      template_file: "templates/daily.html"
      include_sections:
        - cluster_overview
        - health_summary
        - resource_usage
        - alerts_summary
    - name: "security_audit"
      template_file: "templates/security.html"
      include_sections:
        - security_findings
        - compliance_status
        - recommendations

integrations:
  prometheus:
    enabled: false
    endpoint: "http://prometheus:9090"
    scrape_interval: "15s"
  grafana:
    enabled: false
    url: "http://grafana:3000"
    api_key: "${GRAFANA_API_KEY}"
  elk:
    enabled: false
    elasticsearch_url: "http://elasticsearch:9200"
    index_pattern: "k8s-reporter-*"

performance:
  max_concurrent_requests: 10
  cache:
    enabled: true
    ttl: "5m"
    max_size_mb: 100
  database:
    type: "sqlite"  # sqlite, postgres, mysql
    connection_string: "./data/reporter.db"
    max_connections: 10
    max_idle_connections: 5

logging:
  level: "info"  # debug, info, warn, error
  format: "json"  # json, text
  output: "stdout"  # stdout, file
  file_config:
    path: "./logs/reporter.log"
    max_size_mb: 100
    max_backups: 3
    max_age_days: 7
```

## Customizing Alerts

Alerts can be fully customized to align with organizational policies. You can specify thresholds for different severity levels and define multiple notification channels.

### Example Alert Settings

```yaml
alerts:
  enabled: true
  critical_threshold: 5  # Threshold for critical issues
  warning_threshold: 10  # Threshold for warnings
  channels:
    emails:
      - email: "ops-team@yourcompany.com"
      - email: "admin-team@yourcompany.com"
    webhooks:
      - url: "https://api.youralertsystem.com/notifications"
```

## Integration Options

k8s-reporter can be integrated with various external systems for seamless operation and notification delivery.

### Example Integrations

```yaml
integrations:
  slack:
    webhook_url: "https://hooks.slack.com/services/EXAMPLE/WEBHOOK"
  pagerduty:
    service_key: "your-pagerduty-service-key"
  email:
    smtp:
      server: "smtp.yourcompany.com"
      port: 587
      auth:
        user: "smtp-user"
        password: "smtp-password"
```

## Advanced Configuration

### Multi-Tenancy Support

To support multiple users, enable authentication and define multiple user profiles:

```yaml
authentication:
  enabled: true
  users:
    - username: "user1"
      password: "password1"
    - username: "user2"
      password: "password2"
```

### Data Retention Policies

Define how long data and reports are stored before being purged:

```yaml
reports:
  retention_days: 30  # Retain reports for 30 days
  max_size_mb: 1000   # Maximum allowed size for report directory
```

## Troubleshooting Configuration

- **Invalid YAML**: Ensure YAML syntax is correct. Use a validator if necessary.
- **Auth Issues**: Double-check usernames and passwords.
- **Network Problems**: Verify network settings and firewall rules.

## Conclusion

With configurable options, k8s-reporter can be adapted to a variety of environments and requirements. For further assistance, contact support@yourcompany.com or refer to the official documentation.
