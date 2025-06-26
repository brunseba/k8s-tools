# 🧩 k8s-reporter Examples

This document covers various example scenarios demonstrating how to effectively utilize k8s-reporter for monitoring and reporting on Kubernetes clusters.

## Quick Start Examples

### Basic Dashboard Setup

```bash
# Start k8s-reporter using default configuration
k8s-reporter start --config ./configs/default-reporter-config.yaml
```

### Custom Port Configuration

```yaml
server:
  port: 9090 # Change to your desired port

# Start with custom port
k8s-reporter start --config ./configs/custom-port-config.yaml
```

### Enabling TLS

To secure the dashboard with TLS, edit your configuration as follows:

```yaml
server:
  tls:
    enabled: true
    cert_file: "/path/to/cert.pem"
    key_file: "/path/to/key.pem"
```

Start the dashboard:

```bash
k8s-reporter start --config ./configs/tls-config.yaml
```

## Real-World Scenarios

### Multi-cluster Management

Manage views from different clusters using context switching:

```bash
# Configure multiple contexts
kubectl config use-context development
k8s-reporter start --config ./configs/dev-cluster-config.yaml

kubectl config use-context production
k8s-reporter start --config ./configs/prod-cluster-config.yaml
```

### Security Compliance Dashboard

Monitor security settings and compliance:

```yaml
alerts:
  enabled: true
  rules:
    - name: "compliance_violation"
      condition: "is_compliant == false"
      severity: "critical"
      channels:
        - type: "email"
          config:
            to: ["security-team@yourcompany.com"]
```

### Historical Data Analysis

Enable persistence for long-term analysis:

```yaml
performance:
  database:
    type: "sqlite"
    connection_string: "./data/history.db"
    max_connections: 20
```

## CI/CD Integration

### GitHub Actions Example

Automate reporting with a GitHub Actions workflow:

```yaml
name: k8s-report

on:
  schedule:
    - cron: "0 0 * * 0" # Weekly report

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup k8s-reporter
        run: |
          curl -LO https://github.com/your-org/k8s-reporter/releases/latest/download/k8s-reporter-linux
          chmod +x k8s-reporter-linux
          sudo mv k8s-reporter-linux /usr/local/bin/k8s-reporter
      - name: Generate report
        run: |
          k8s-reporter generate --format html --output weekly-report.html
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: weekly-report
          path: weekly-report.html
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'curl -LO https://github.com/your-org/k8s-reporter/releases/latest/download/k8s-reporter-linux'
                sh 'chmod +x k8s-reporter-linux'
                sh 'sudo mv k8s-reporter-linux /usr/local/bin/k8s-reporter'
            }
        }
        stage('Report') {
            steps {
                sh 'k8s-reporter generate --format html --output jenkins-report.html'
                archiveArtifacts artifacts: 'jenkins-report.html'
            }
        }
    }
}
```

## Advanced Use Cases

### Configuring Dynamic Dashboards

Define dynamic dashboards using environment-specific settings:

```yaml
environment:
  variables:
    - name: "ENV_NAME"
      value: "staging"

dashboard:
  title: "Dashboard - ${ENV_NAME}"
  theme: "dark"
```

### Building Custom Reports

Create personalized report layouts:

```yaml
reports:
  templates:
    - name: "custom_operations_report"
      sections:
        - resource_summary
        - performance_insights
        - custom_script_output
```

## Conclusion

These examples are designed to illustrate the versatility of k8s-reporter in various contexts. For further information, please explore the official [documentation](http://yourcompany.com/docs/k8s-reporter) or join the community discussions.
