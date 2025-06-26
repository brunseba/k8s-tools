# 🔍 k8s-analyzer Overview

The `k8s-analyzer` is a command-line tool designed to provide deep insight into Kubernetes cluster resources, relationships, and configurations. It extracts, analyzes, and maps Kubernetes resources, providing outputs in various formats for further analysis and visualization.

## Key Features

- **Multi-source Data Collection**: Supports parsing from `kubectl` exports, YAML files, and directories.
- **Resource Relationship Mapping**: Automatically detects dependencies and connections between resources.
- **Health Assessment**: Evaluates health status and identifies configuration issues.
- **Flexible Output Formats**: Exports results to JSON, SQLite, and CSV.
- **Comprehensive Command Suite**: Includes commands for parsing, analyzing, graphing, and exporting data.

## Functional Flow

1. **Input Layer**: Accepts JSON/YAML from `kubectl` or other defined sources.
2. **Parser Layer**: Converts input files into structured data models.
3. **Data Model Layer**: Creates data models for resources and relationships.
4. **Analysis Layer**: Maps relationships and conducts health assessments.
5. **Output Layer**: Exports data to JSON, SQLite, CSV, and HTML formats.

## CLI Commands

### Basic Commands
- `parse [file]`: Parse resource data from file.
- `analyze [file]`: Analyze resources and relationships.
- `report [file]`: Generate comprehensive HTML analysis report.
- `validate [file]`: Validate resource configurations.

### Export Commands
- `export_sqlite [file] [db]`: Export data to SQLite database.
- `export_csv [file] [dir]`: Export data to CSV files.

## Example Usage

```bash
# Parse and analyze a cluster export
k8s-analyzer parse cluster-export.json
k8s-analyzer analyze cluster-export.json

# Export to a SQLite database
k8s-analyzer export_sqlite cluster-export.json cluster-analysis.db

# Generate an HTML report
k8s-analyzer report cluster-export.json --output cluster-report.html
```

## Advanced Use Cases

### Batch Processing

```bash
# Analyze all YAML files in a directory
k8s-analyzer batch-analyze ./manifests --output batch-report.json

# Export an entire directory to SQLite
k8s-analyzer export_directory_sqlite ./manifests cluster.db
```

### Namespace Filtering

```bash
# Analyze resources in a specific namespace
k8s-analyzer analyze cluster-export.json --namespace production
```

### Health and Compliance

```bash
# Validate overall configuration health
k8s-analyzer validate cluster-export.json

# Generate compliance report
k8s-analyzer report cluster-export.json --output compliance-report.html
```

## Supported Resource Types

- **Pod** - Running workloads
- **Service** - Network endpoints
- **ConfigMap** - Configuration data
- **PersistentVolumeClaim** - Storage requests
- **Ingress** - External access
- **ServiceAccount** - Pod identity and authentication

## Development Workflow

```bash
# Clone the repository
git clone https://github.com/k8s-tools/k8s-analyzer.git
cd k8s-analyzer

# Install development dependencies
uv sync --extras dev

# Run tests
uv run pytest

# Format and lint code
uv run black src tests
uv run flake8 src tests
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** and clone your fork.
2. **Create a feature branch** for your changes.
3. **Develop and test** your features.
4. **Submit a pull request** to merge your changes.

