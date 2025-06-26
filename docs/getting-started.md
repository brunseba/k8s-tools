# 🚀 Getting Started with K8s Tools

This guide will walk you through installing and using K8s Tools to analyze your Kubernetes clusters.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed on your system
- **kubectl** configured for your Kubernetes cluster
- **UV package manager** (recommended) or pip
- **Git** for cloning the repository

### Installing UV Package Manager

UV is the recommended package manager for fast and reliable Python environment management:

```bash
# Install UV (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using Homebrew (macOS)
brew install uv

# Or using pip
pip install uv
```

## Installation Methods

### Option 1: UV Tool Installation (Recommended)

This is the fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/k8s-tools/k8s-tools.git
cd k8s-tools

# Install both tools globally
uv tool install ./k8s-analyzer
uv tool install ./k8s-reporter

# Verify installation
k8s-analyzer --version
k8s-reporter --version
```

### Option 2: Development Installation

For development or customization:

```bash
# Clone the repository
git clone https://github.com/k8s-tools/k8s-tools.git
cd k8s-tools

# Install k8s-analyzer
cd k8s-analyzer
uv sync
uv run k8s-analyzer --help

# Install k8s-reporter
cd ../k8s-reporter
uv sync
uv run streamlit run src/k8s_reporter/app.py
```

### Option 3: Traditional pip Installation

```bash
# Install from source
git clone https://github.com/k8s-tools/k8s-tools.git
cd k8s-tools

# Install k8s-analyzer
cd k8s-analyzer
pip install -e .

# Install k8s-reporter
cd ../k8s-reporter
pip install -e .
```

## First Analysis

### Step 1: Export Cluster Data

First, export your Kubernetes cluster data using kubectl:

```bash
# Export all cluster resources to JSON
kubectl get all,nodes,pv,pvc,configmaps,secrets,serviceaccounts,rolebindings,ingress \
  -o json > cluster-export.json

# Or export to YAML
kubectl get all,nodes,pv,pvc,configmaps,secrets,serviceaccounts,rolebindings,ingress \
  -o yaml > cluster-export.yaml
```

### Step 2: Analyze with k8s-analyzer

```bash
# Basic analysis and export to SQLite
k8s-analyzer sqlite cluster-export.json --output cluster-analysis.db

# Or analyze and export to CSV
k8s-analyzer csv cluster-export.json --output-dir ./reports

# Generate comprehensive HTML report
k8s-analyzer report cluster-export.json --output cluster-report.html
```

### Step 3: Launch the Web Dashboard

```bash
# Launch the interactive web interface
k8s-reporter --database cluster-analysis.db

# Open http://localhost:8501 in your browser
```

## Understanding the Output

### SQLite Database

The SQLite database contains structured data about your cluster:

- **resources** table: All Kubernetes resources with metadata
- **relationships** table: Resource dependencies and connections
- **analysis_summary** table: High-level cluster statistics

### Dashboard Views

The web interface provides several analysis views:

1. **📊 Cluster Overview** - Health metrics and resource distribution
2. **🔒 Security Analysis** - RBAC and security posture insights
3. **🏷️ Namespace Analysis** - Per-namespace breakdowns
4. **❤️ Health Dashboard** - Resource health monitoring
5. **🔗 Relationship Analysis** - Resource dependencies
6. **⚡ Resource Efficiency** - Optimization opportunities
7. **💾 Storage Analysis** - Storage consumption tracking
8. **⏰ Temporal Analysis** - Resource lifecycle patterns

## Common Use Cases

### Health Monitoring

```bash
# Quick cluster health check
k8s-analyzer analyze cluster-export.json

# Generate health report
k8s-analyzer validate cluster-export.json
```

### Multi-cluster Analysis

```bash
# Analyze multiple clusters
k8s-analyzer sqlite cluster1.json cluster2.json --output multi-cluster.db

# Compare clusters in the dashboard
k8s-reporter --database multi-cluster.db
```

### Continuous Monitoring

```bash
#!/bin/bash
# daily-analysis.sh - Automated daily cluster analysis

DATE=$(date +%Y-%m-%d)
kubectl get all,nodes,pv,pvc,configmaps,secrets,serviceaccounts,rolebindings,ingress \
  -o json > "cluster-export-${DATE}.json"

k8s-analyzer sqlite "cluster-export-${DATE}.json" \
  --output "cluster-analysis-${DATE}.db"

echo "Analysis complete: cluster-analysis-${DATE}.db"
```

## Configuration

### Environment Variables

```bash
# k8s-analyzer configuration
export K8S_ANALYZER_OUTPUT_DIR="./analysis"
export K8S_ANALYZER_LOG_LEVEL="INFO"

# k8s-reporter configuration
export K8S_REPORTER_HOST="0.0.0.0"
export K8S_REPORTER_PORT="8501"
export K8S_REPORTER_DATABASE="./cluster.db"
```

### Custom Analysis

```bash
# Filter by namespace
k8s-analyzer sqlite cluster-export.json \
  --namespace production \
  --output production-analysis.db

# Filter by resource types
k8s-analyzer csv cluster-export.json \
  --include-kinds Pod,Service,Deployment \
  --output-dir filtered-reports

# Exclude system namespaces
k8s-analyzer sqlite cluster-export.json \
  --exclude-namespaces kube-system,kube-public \
  --output user-analysis.db
```

## Troubleshooting

### Common Issues

#### 1. kubectl Export Errors

```bash
# Check cluster connectivity
kubectl cluster-info

# Verify permissions
kubectl auth can-i get pods --all-namespaces
```

#### 2. Large Cluster Performance

```bash
# Use batch processing for large clusters
k8s-analyzer sqlite cluster-export.json \
  --batch-size 100 \
  --output large-cluster.db
```

#### 3. Memory Issues

```bash
# Process files individually for very large clusters
k8s-analyzer sqlite pods.json --output pods.db
k8s-analyzer sqlite services.json --output services.db
# Then merge databases if needed
```

#### 4. Web Interface Issues

```bash
# Check if port is available
netstat -an | grep 8501

# Use different port
k8s-reporter --database cluster.db --port 8080

# Enable debug mode
k8s-reporter --database cluster.db --debug
```

### Getting Help

```bash
# View available commands
k8s-analyzer --help
k8s-reporter --help

# Get specific command help
k8s-analyzer sqlite --help
k8s-analyzer analyze --help
```

## Next Steps

Now that you have K8s Tools installed and running:

1. **[Explore k8s-analyzer](analyzer/overview.md)** - Learn about advanced analysis features
2. **[Master k8s-reporter](reporter/overview.md)** - Discover all dashboard capabilities
3. **[Understand Analysis Views](analysis-views/overview.md)** - Deep dive into each analysis type
4. **[Set up Development](development/setup.md)** - Contribute to the project

## Performance Tips

### For Large Clusters

- Use batch processing with `--batch-size` parameter
- Export specific namespaces separately
- Consider using multiple smaller exports instead of one large file

### For Regular Monitoring

- Set up automated daily/weekly exports
- Use filesystem monitoring to trigger analysis on changes
- Implement retention policies for historical data

### For CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Cluster Analysis
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install K8s Tools
        run: |
          uv tool install ./k8s-analyzer
          uv tool install ./k8s-reporter
      - name: Analyze Cluster
        run: |
          kubectl get all -o json > cluster.json
          k8s-analyzer sqlite cluster.json --output analysis.db
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: cluster-analysis
          path: analysis.db
```

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Search [existing issues](https://github.com/k8s-tools/k8s-tools/issues)
3. Create a [new issue](https://github.com/k8s-tools/k8s-tools/issues/new) with:
   - Your environment details
   - Steps to reproduce
   - Error messages
   - Sample data (anonymized)
