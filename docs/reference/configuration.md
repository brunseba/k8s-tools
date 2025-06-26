# ⚙️ Configuration Reference

This document serves as a reference for understanding the configuration settings for k8s-analyzer and k8s-reporter, enabling users to customize their environment according to specific needs and requirements.

## Configuration Structure

The primary configuration files are structured in YAML format, which allows for human-readable and easily modifiable settings. Key sections include:

- **Server Settings**: Configure network, ports, and TLS options.
- **Authentication**: Set up user authentication and access control.
- **Resources**: Define resource polling intervals, types, and inclusion settings.
- **Alerts**: Configure alert rules and notification channels.
- **Reports**: Manage report formats, schedules, and storage.
- **Integrations**: Set up connections with external services.

## Server Settings

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  tls:
    enabled: false
    cert_file: ""
    key_file: ""
```

- **host**: Server host address, usually set to 0.0.0.0 to listen on all interfaces.
- **port**: Port on which the server will run.
- **tls**: TLS configuration for securing the dashboard.

## Authentication

```yaml
authentication:
  enabled: true
  type: "basic"
  users:
    - username: "admin"
      password: "securepassword"
```

- **enabled**: Enable or disable authentication.
- **type**: Type of authentication (basic, oauth2, etc.).
- **users**: List of user credentials with roles.

## Alerts

```yaml
alerts:
  enabled: true
  rules:
    - name: "pod_failures"
      condition: "pod_status == 'Failed'"
      severity: "critical"
      channels:
        - email: "alerts@company.com"
```

- **enabled**: Activate the alerting system.
- **rules**: Define alert rules based on specific conditions.
- **channels**: Configure notification channels.

## Integrations

```yaml
integrations:
  slack:
    webhook_url: "https://hooks.slack.com/services/EXAMPLE/WEBHOOK"
  pagerduty:
    service_key: "your-pagerduty-service-key"
```

- **slack**: Slack integration settings.
- **pagerduty**: PagerDuty integration settings.

## Advanced Configuration

### Dynamic Resource Polling

Configure dynamic polling based on resource types:

```yaml
resources:
  refresh_interval: 30s
  types:
    - pods
    - services
```

### Customized Widgets

Add custom widgets to the dashboard:

```yaml
dashboard:
  widgets:
    - type: "custom_chart"
      data: "cpu_usage"
```

## Best Practices

- Regularly update configuration files to adapt to changes in the cluster environment.
- Secure configuration files with appropriate permissions.
- Test configuration changes in a staging environment before applying them to production.

## Conclusion

By providing detailed configuration references, users can tailor k8s-tools to their specific needs, enhancing the tool's flexibility and integration within diverse environments.
