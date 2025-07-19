# Basic Usage

This guide provides basic usage examples for K8s Tools, covering initial setup and common operations using both k8s-analyzer and k8s-reporter.

## Initial Setup

Ensure K8s Tools components are installed:

```bash
# Using pipx (recommended)
pipx install k8s-analyzer
pipx install k8s-reporter

# Using pip
pip install k8s-analyzer
pip install k8s-reporter
```

Check the versions to verify installation:

```bash
k8s-analyzer --help
k8s-reporter --help
```

## k8s-analyzer: Basic Operations

### Parsing Kubernetes Exports

Parse a kubectl export file to extract resources:

```bash
# Parse a single file
k8s-analyzer parse cluster-export.yaml

# Parse with additional files
k8s-analyzer parse cluster-export.yaml --additional deployment1.yaml --additional service1.yaml

# Save parsed results to JSON
k8s-analyzer parse cluster-export.yaml --output parsed-resources.json
```

### Analyzing Resource Relationships

Analyze Kubernetes resources and build relationship mappings:

```bash
# Basic analysis
k8s-analyzer analyze cluster-export.yaml

# Analysis with verbose output
k8s-analyzer analyze cluster-export.yaml --verbose

# Save analysis results
k8s-analyzer analyze cluster-export.yaml --output analysis-results.json
```

### Generating HTML Reports

Create comprehensive HTML reports from analyzed data:

```bash
# Generate report with default name
k8s-analyzer report cluster-export.yaml

# Custom report name
k8s-analyzer report cluster-export.yaml --output custom-report.html
```

### Visualizing Resource Relationships

Display resource relationship graphs:

```bash
# Show all relationships
k8s-analyzer graph cluster-export.yaml

# Filter by namespace
k8s-analyzer graph cluster-export.yaml --namespace production

# Filter by resource type
k8s-analyzer graph cluster-export.yaml --type Deployment
```

### Validating Configurations

Validate resource configurations and identify issues:

```bash
k8s-analyzer validate cluster-export.yaml --verbose
```

## Working with Directories

### Scanning for Kubernetes Files

Discover and list Kubernetes files in a directory:

```bash
# List files in current directory
k8s-analyzer list-files .

# List files with custom patterns
k8s-analyzer list-files ./k8s-configs --pattern "*.yaml" --pattern "*.yml"

# Non-recursive scan
k8s-analyzer list-files ./manifests --no-recursive
```

### Batch Processing

Process multiple Kubernetes files at once:

```bash
# Scan and parse directory
k8s-analyzer scan ./k8s-manifests

# Batch analyze directory
k8s-analyzer batch-analyze ./k8s-manifests --output batch-results.json

# Limit number of files processed
k8s-analyzer batch-analyze ./k8s-manifests --max-files 50
```

## SQLite Database Operations

### Exporting to SQLite

Export analyzed data to SQLite for persistent storage:

```bash
# Export single file
k8s-analyzer export-sqlite cluster-export.yaml cluster.db

# Export multiple files
k8s-analyzer export-multiple-sqlite file1.yaml file2.yaml file3.yaml --database cluster.db

# Export entire directory
k8s-analyzer export-directory-sqlite ./k8s-configs cluster.db
```

### Querying SQLite Database

Query the SQLite database for specific resources:

```bash
# Query all resources
k8s-analyzer query-db cluster.db

# Filter by resource kind
k8s-analyzer query-db cluster.db --kind Deployment

# Filter by namespace
k8s-analyzer query-db cluster.db --namespace production

# Filter by health status
k8s-analyzer query-db cluster.db --health error

# Show only resources with issues
k8s-analyzer query-db cluster.db --issues
```

### Database Statistics

Get summary statistics from your SQLite database:

```bash
k8s-analyzer db-summary cluster.db
```

### Exporting to CSV

Export SQLite database contents to CSV files:

```bash
k8s-analyzer export-csv cluster.db ./csv-exports/
```

## k8s-reporter: Web Dashboard

### Launching the Web UI

Start the Streamlit-based web dashboard:

```bash
# Launch with default settings
k8s-reporter

# Launch on custom port
k8s-reporter --port 8080

# Launch with custom host
k8s-reporter --host 0.0.0.0 --port 8080
```

### Loading Existing Databases

Pre-load a SQLite database when starting the dashboard:

```bash
k8s-reporter --database cluster.db
```

### Production Deployment

Run in headless mode for production:

```bash
# Headless mode (no browser auto-open)
k8s-reporter --headless --host 0.0.0.0 --port 8080

# With debug mode for troubleshooting
k8s-reporter --debug --database cluster.db
```

## Common Workflows

### Analyze and Visualize

```bash
# 1. Export cluster state
kubectl get all --all-namespaces -o yaml > cluster-export.yaml

# 2. Analyze the export
k8s-analyzer analyze cluster-export.yaml --output analysis.json

# 3. Export to SQLite for persistence
k8s-analyzer export-sqlite cluster-export.yaml cluster.db

# 4. Launch web dashboard
k8s-reporter --database cluster.db
```

### Batch Processing Workflow

```bash
# 1. Process directory of manifest files
k8s-analyzer batch-analyze ./kubernetes-manifests --output batch-analysis.json

# 2. Export to SQLite
k8s-analyzer export-directory-sqlite ./kubernetes-manifests manifests.db

# 3. Generate HTML report
k8s-analyzer report ./kubernetes-manifests/app-deployment.yaml --output deployment-report.html

# 4. Query for specific issues
k8s-analyzer query-db manifests.db --issues --limit 20
```

### Validation and Health Check

```bash
# 1. Validate configurations
k8s-analyzer validate cluster-export.yaml

# 2. Check relationship graph
k8s-analyzer graph cluster-export.yaml --namespace kube-system

# 3. Export for further analysis
k8s-analyzer export-csv cluster.db ./health-reports/
```

## Tips and Best Practices

### Performance Optimization

- Use `--max-files` to limit processing when working with large directories
- Enable `--verbose` for debugging but disable for production scripts
- Use SQLite export for persistent storage of analysis results

### File Organization

```bash
# Organize exports by date
mkdir -p exports/$(date +%Y-%m-%d)
k8s-analyzer analyze cluster-export.yaml --output exports/$(date +%Y-%m-%d)/analysis.json
```

### Automation Scripts

```bash
#!/bin/bash
# Daily cluster analysis script
DATE=$(date +%Y-%m-%d)
EXPORT_DIR="daily-exports/$DATE"

mkdir -p "$EXPORT_DIR"

# Export cluster state
kubectl get all --all-namespaces -o yaml > "$EXPORT_DIR/cluster-export.yaml"

# Analyze and export to SQLite
k8s-analyzer analyze "$EXPORT_DIR/cluster-export.yaml" --output "$EXPORT_DIR/analysis.json"
k8s-analyzer export-sqlite "$EXPORT_DIR/cluster-export.yaml" "$EXPORT_DIR/cluster.db"

# Generate HTML report
k8s-analyzer report "$EXPORT_DIR/cluster-export.yaml" --output "$EXPORT_DIR/report.html"

echo "Analysis complete for $DATE"
```

## Troubleshooting

### Common Issues

**File parsing errors**: Ensure YAML/JSON files are valid
```bash
# Test file validity
yaml-lint cluster-export.yaml
```

**SQLite database locked**: Close any open database connections
```bash
# Check if database is accessible
k8s-analyzer db-summary cluster.db
```

**Web UI not starting**: Check if port is available
```bash
# Test different port
k8s-reporter --port 8502
```

## Getting Support

- Check command help: `k8s-analyzer [command] --help`
- Enable verbose logging: `--verbose` flag
- Review generated logs and error messages
- [GitHub Issues](https://github.com/k8s-tools/k8s-tools/issues)

## Related Documentation

- [Advanced Workflows](advanced-workflows.md)
- [Multi-cluster Analysis](multi-cluster.md)
- [Custom Dashboards](custom-dashboards.md)
