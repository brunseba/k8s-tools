# 🖥️ k8s-reporter Dashboard Guide

This guide provides a comprehensive overview of the k8s-reporter dashboard, detailing features, configuration, and usage for efficient monitoring of Kubernetes clusters.

## Overview

The k8s-reporter dashboard is designed to provide real-time visualization of your Kubernetes cluster's health, performance, and compliance. It integrates seamlessly with k8s-analyzer to present thorough insights into resources and their relationships.

### Key Features
- **Real-time Monitoring:** Display current state of all cluster resources with updates.
- **Health Status Indicators:** Easily discern healthy, warning, and error states.
- **Resource Graphs and Tables:** Visualize dependencies and resource allocation.
- **Compliance and Security Checks:** Identify and manage compliance issues.
- **Custom Reports and Alerts:** Generate and distribute custom reports with configurable alerts.

## Getting Started

### Installing Dashboard

1. **Download** the latest version of k8s-reporter.
   ```bash
   curl -LO https://github.com/your-org/k8s-reporter/releases/latest/download/k8s-reporter-linux
   chmod +x k8s-reporter-linux
   sudo mv k8s-reporter-linux /usr/local/bin/k8s-reporter
   ```

2. **Configure** access to your Kubernetes context.
   ```bash
   kubectl config use-context your-cluster-context
   ```

3. **Run** the k8s-reporter with default settings.
   ```bash
   k8s-reporter start --config ./configs/default-reporter-config.yaml
   ```

### Accessing the Dashboard

Once started, access the dashboard via your browser:
- **URL**: http://localhost:8080
- Default **credentials**: 
  - **Username**: admin
  - **Password**: admin123

## Configuration

The dashboard configuration is defined in a YAML file, which allows extensive customization of displayed data, update intervals, and alert settings.

### Sample Configuration

```yaml
server:
  port: 8080
  host: "0.0.0.0"
authentication:
  username: "admin"
  password: "change-this-password"

resources:
  update_interval: 60s # How often to refresh metrics
  show_health_status: true
  show_relationships: true

alerts:
  enable: true
  critical_threshold: 5
  notification_channels:
    - email: "alerts@yourcompany.com"
    - webhook: "https://hooks.yourservice.com/api/alerts"

reports:
  format: "html"
  directory: "./reports"
  retention_period: 30d
  include_graphs: true

```

## Customization

### Adding Widgets

Widgets can be added to display custom metrics or information:

```yaml
widgets:
  - type: "metric_chart"
    title: "CPU Usage"
    metric: "kube_pod_container_resource_requests_cpu_cores"
    timeframe: "24h"
  - type: "status_list"
    title: "Critical Pods"
    filter: "health_status=error"
```

### Integration with Other Tools

Integrate with Slack, PagerDuty, etc., for notifications or data exports.
```yaml
integrations:
  slack:
    webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  pagerduty:
    service_key: "your-service-key"
```

## Usage Tips

- **Filter Views:** Use search and filter options to focus on specific namespaces or resource types.
- **Drill Down:** Click on resources in charts to view detailed metadata and health assessments.
- **Custom Alerts:** Set thresholds for different resource types to receive timely alerts.
- **Historical Data:** Access historical trends for informed decision-making about capacity planning and scaling.

## Troubleshooting

- **Dashboard Not Loading:** Verify network settings and ensure the k8s-reporter service is running.
- **Authentication Issues:** Reset credentials in the configuration YAML.
- **Data Not Updating:** Check Kubernetes context configuration and network connectivity.

## Further Assistance
For more help, refer to our [support page](http://support.yourcompany.com) or contact us at support@yourcompany.com.

This guide ensures you maximize the benefits of the k8s-reporter dashboard for Kubernetes monitoring and management.
