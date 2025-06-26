# ❓ Frequently Asked Questions (FAQ)

This FAQ addresses common questions about k8s-analyzer and k8s-reporter, providing quick answers to help users get started and resolve common issues.

## General Questions

### What are k8s-analyzer and k8s-reporter?

**k8s-analyzer** is a command-line tool for analyzing Kubernetes cluster configurations and resources. It provides insights into resource health, relationships, security compliance, and operational metrics.

**k8s-reporter** is a web-based dashboard that provides real-time visualization and reporting capabilities for Kubernetes clusters, built on top of analysis data from k8s-analyzer.

### What are the system requirements?

- **Operating System**: Linux, macOS, or Windows
- **Kubernetes**: Compatible with Kubernetes 1.19+
- **Resources**: Minimum 512MB RAM, 1GB disk space
- **Network**: Access to Kubernetes API server

### How do I install k8s-tools?

```bash
# Download latest releases
curl -LO https://github.com/your-org/k8s-analyzer/releases/latest/download/k8s-analyzer-linux
curl -LO https://github.com/your-org/k8s-reporter/releases/latest/download/k8s-reporter-linux

# Make executable and install
chmod +x k8s-analyzer-linux k8s-reporter-linux
sudo mv k8s-analyzer-linux /usr/local/bin/k8s-analyzer
sudo mv k8s-reporter-linux /usr/local/bin/k8s-reporter
```

## k8s-analyzer Questions

### How do I analyze my cluster?

```bash
# Analyze current cluster
k8s-analyzer analyze

# Analyze specific namespace
k8s-analyzer analyze --namespace production

# Parse local YAML files
k8s-analyzer parse ./manifests/ --output cluster-state.json
```

### What output formats are supported?

k8s-analyzer supports multiple output formats:
- **JSON**: Machine-readable structured data
- **HTML**: Interactive web reports
- **CSV**: Spreadsheet-compatible format
- **SQLite**: Database format for complex queries

### Can I analyze multiple clusters?

Yes! Switch between clusters using kubectl contexts:

```bash
kubectl config use-context cluster-1
k8s-analyzer analyze --output cluster-1-analysis.json

kubectl config use-context cluster-2
k8s-analyzer analyze --output cluster-2-analysis.json
```

### How do I filter analysis results?

Use filtering options to focus on specific resources:

```bash
# Filter by namespace
k8s-analyzer analyze --namespace-filter "production,staging"

# Filter by resource type
k8s-analyzer analyze --resource-types "pods,services"

# Filter by health status
k8s-analyzer report analysis.json --filter "health_status=error"
```

## k8s-reporter Questions

### How do I start the dashboard?

```bash
# Start with default configuration
k8s-reporter start

# Start with custom configuration
k8s-reporter start --config ./config.yaml
```

### What is the default login?

Default credentials are:
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change these credentials before deploying to production!

### How do I configure alerts?

Edit your configuration file:

```yaml
alerts:
  enabled: true
  rules:
    - name: "pod_failures"
      condition: "pod_status == 'Failed'"
      severity: "critical"
      channels:
        - email: "alerts@company.com"
        - slack: "#alerts"
```

### Can I customize the dashboard?

Yes! You can customize:
- **Themes**: Light/dark mode
- **Widgets**: Add custom charts and metrics
- **Layout**: Rearrange dashboard components
- **Branding**: Add company logos and colors

## Integration Questions

### How do I integrate with CI/CD?

**GitHub Actions Example:**
```yaml
- name: Analyze Kubernetes manifests
  run: |
    k8s-analyzer parse ./k8s/ --output analysis.json
    k8s-analyzer validate analysis.json --strict
```

**Jenkins Pipeline:**
```groovy
stage('K8s Analysis') {
    steps {
        sh 'k8s-analyzer analyze --output analysis.json'
        sh 'k8s-analyzer report analysis.json --format html --output report.html'
        publishHTML([allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true, reportDir: '.', reportFiles: 'report.html', reportName: 'K8s Analysis Report'])
    }
}
```

### How do I integrate with monitoring systems?

k8s-tools can integrate with:
- **Prometheus**: Export metrics for monitoring
- **Grafana**: Create custom dashboards
- **ELK Stack**: Log analysis and visualization
- **Slack/PagerDuty**: Alert notifications

### Can I use custom metrics?

Yes! Define custom metrics in your configuration:

```yaml
custom_metrics:
  - name: "app_response_time"
    query: "avg(response_time_seconds) by (app)"
    threshold: 2.0
```

## Performance Questions

### How much data can k8s-analyzer handle?

k8s-analyzer is optimized for large clusters:
- **Resources**: 10,000+ resources per cluster
- **Memory**: Efficient streaming processing
- **Performance**: Parallel analysis for speed

### How often should I run analysis?

Recommended frequencies:
- **Development**: Every commit or daily
- **Staging**: Daily or before deployments
- **Production**: Daily for health checks, weekly for comprehensive analysis

### Can I schedule automatic reports?

Yes! Use cron jobs or CI/CD schedulers:

```bash
# Daily analysis at 6 AM
0 6 * * * /usr/local/bin/k8s-analyzer analyze --output /reports/daily-$(date +\%Y\%m\%d).json
```

## Security Questions

### Is my cluster data secure?

k8s-tools follow security best practices:
- **Local Processing**: Analysis runs locally, no data sent externally
- **RBAC**: Respects Kubernetes RBAC permissions
- **TLS**: Dashboard supports TLS encryption
- **Authentication**: Configurable user authentication

### What permissions are required?

Minimum RBAC permissions:
```yaml
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list"]
```

## Troubleshooting Questions

### Why is analysis failing?

Common causes:
1. **Permissions**: Check RBAC permissions
2. **Connectivity**: Verify cluster access
3. **Resources**: Ensure sufficient memory/disk
4. **Configuration**: Validate YAML syntax

### Dashboard not loading?

Check these items:
1. **Service Status**: Is k8s-reporter running?
2. **Port Access**: Is port 8080 accessible?
3. **Firewall**: Are there blocking rules?
4. **Logs**: Check error messages in logs

### How do I get support?

- **Documentation**: Check the official docs
- **Issues**: Report bugs on GitHub
- **Community**: Join discussions in forums
- **Commercial**: Contact support for enterprise versions

## Performance Optimization

### How can I improve analysis speed?

1. **Filter Resources**: Analyze only needed resources
2. **Parallel Processing**: Use multiple workers
3. **Incremental Analysis**: Only analyze changes
4. **Caching**: Enable result caching

```bash
# Optimized analysis
k8s-analyzer analyze \
  --workers 4 \
  --cache-enabled \
  --incremental \
  --namespace-filter "production"
```

### How do I reduce memory usage?

1. **Batch Processing**: Process resources in batches
2. **Streaming**: Use streaming for large datasets
3. **Compression**: Enable output compression
4. **Cleanup**: Regular cleanup of old data

## Advanced Usage

### Can I extend k8s-tools?

Yes! k8s-tools support:
- **Custom Plugins**: Add custom analysis logic
- **API Extensions**: Build on top of the API
- **Custom Reports**: Create custom report templates
- **Webhooks**: Integrate with external systems

### How do I backup analysis data?

```bash
# Backup SQLite database
cp analysis.db backup-$(date +%Y%m%d).db

# Export to multiple formats
k8s-analyzer export analysis.json --format json,csv,html
```

This FAQ covers the most common questions about k8s-tools. For more specific questions, please refer to the detailed documentation or contact support.
