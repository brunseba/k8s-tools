# Kubernetes Resource Analyzer

A powerful Python tool for analyzing Kubernetes cluster exports and building comprehensive resource relationship mappings.

## 🎯 Features

- **Parse kubectl exports** - Support for JSON and YAML formats
- **Resource relationship mapping** - Automatically detect dependencies and connections
- **Health assessment** - Identify resource issues and configuration problems
- **Multiple output formats** - JSON, HTML reports, and interactive CLI
- **Rich CLI interface** - Beautiful terminal output with colors and tables
- **Comprehensive analysis** - Support for Pods, Services, ConfigMaps, PVCs, Nodes, and more

## 📦 Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone <repository-url>
cd k8s-analyzer
uv sync
```

### Using pip

```bash
pip install -e .
```

## 🚀 Quick Start

### 1. Export your cluster resources

```bash
# Export all resources to JSON
kubectl get all,nodes,pv,pvc,configmaps,secrets,serviceaccounts,rolebindings,ingress -o json > cluster-export.json

# Or export to YAML
kubectl get all,nodes,pv,pvc,configmaps,secrets,serviceaccounts,rolebindings,ingress -o yaml > cluster-export.yaml
```

### 2. Analyze with k8s-analyzer

```bash
# Basic parsing
k8s-analyzer parse cluster-export.json

# Full analysis with relationships
k8s-analyzer analyze cluster-export.json

# Generate HTML report
k8s-analyzer report cluster-export.json --output cluster-report.html

# Display relationship graph
k8s-analyzer graph cluster-export.json --namespace default

# Validate configurations
k8s-analyzer validate cluster-export.json
```

## 🔧 CLI Commands

### `parse`
Parse kubectl export files and extract resources.

```bash
k8s-analyzer parse [FILE] [OPTIONS]

Options:
  -a, --additional [FILES]  Additional files to merge
  -o, --output [PATH]       Output file path (JSON format)
  -v, --verbose            Enable verbose logging
```

### `analyze`
Parse and analyze kubectl exports with relationship mapping.

```bash
k8s-analyzer analyze [FILE] [OPTIONS]

Options:
  -a, --additional [FILES]  Additional files to merge
  -o, --output [PATH]       Output file path (JSON format)
  -v, --verbose            Enable verbose logging
```

### `report`
Generate comprehensive HTML analysis report.

```bash
k8s-analyzer report [FILE] [OPTIONS]

Options:
  -a, --additional [FILES]  Additional files to merge
  -o, --output [PATH]       Output HTML report path
  -v, --verbose            Enable verbose logging
```

### `graph`
Display resource relationship graph.

```bash
k8s-analyzer graph [FILE] [OPTIONS]

Options:
  -a, --additional [FILES]  Additional files to merge
  -n, --namespace [NS]      Filter by namespace
  -t, --type [TYPE]         Filter by resource type
  -v, --verbose            Enable verbose logging
```

### `validate`
Validate resource configurations and identify issues.

```bash
k8s-analyzer validate [FILE] [OPTIONS]

Options:
  -a, --additional [FILES]  Additional files to merge
  -v, --verbose            Enable verbose logging
```

## 📊 Supported Resource Types

### MVP Scope
- **Pod** - Running workloads
- **Service** - Network endpoints  
- **ConfigMap** - Configuration data
- **Node** - Cluster nodes
- **Namespace** - Resource organization
- **PersistentVolume** - Cluster storage
- **PersistentVolumeClaim** - Storage requests
- **RoleBinding** - RBAC permissions
- **Ingress** - External access
- **ServiceAccount** - Pod identity

### Relationship Types
- **OWNS** - Resource owns another (e.g., Deployment owns ReplicaSet)
- **USES** - Resource uses another (e.g., Pod uses ConfigMap)
- **EXPOSES** - Resource exposes another (e.g., Service exposes Pod)
- **BINDS** - Resource binds to another (e.g., PVC binds to PV)
- **REFERENCES** - Resource references another (e.g., Pod references ServiceAccount)
- **DEPENDS_ON** - Resource depends on another (e.g., Pod depends on Node)
- **SELECTS** - Resource selects another (e.g., Service selects Pods)

## 🏗️ Architecture

```
Input Layer     Parser Layer     Data Model      Analysis Layer    Output Layer
┌─────────────┐ ┌──────────────┐ ┌─────────────┐ ┌───────────────┐ ┌─────────────┐
│ JSON Files  │ │   Resource   │ │    Core     │ │   Resource    │ │ CLI Display │
│ YAML Files  │→│    Parser    │→│   Models    │→│   Analyzer    │→│ JSON Export │
│kubectl Exprt│ │  Validator   │ │Relationship │ │  Dependency   │ │HTML Reports │
└─────────────┘ │  Normalizer  │ │   Engine    │ │   Tracker     │ │Visualization│
                └──────────────┘ └─────────────┘ └───────────────┘ └─────────────┘
```

## 💻 Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd k8s-analyzer

# Install with development dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linting
uv run black src tests
uv run isort src tests
uv run flake8 src tests
uv run mypy src
```

### Project Structure

```
k8s-analyzer/
├── src/k8s_analyzer/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data models and relationships
│   ├── parser.py            # Resource parsing logic
│   ├── analyzer.py          # Relationship analysis engine
│   └── cli.py               # CLI interface
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 📈 Usage Examples

### Basic Analysis

```python
from k8s_analyzer import parse_kubectl_export, ResourceAnalyzer

# Parse cluster export
cluster_state = parse_kubectl_export("cluster-export.json")

# Analyze relationships
analyzer = ResourceAnalyzer()
analyzed_state = analyzer.analyze_cluster(cluster_state)

# Access results
print(f"Found {len(analyzed_state.resources)} resources")
print(f"Found {len(analyzed_state.relationships)} relationships")
```

### Custom Analysis

```python
from k8s_analyzer import ClusterState, ResourceAnalyzer

# Load existing analysis
with open("analysis-results.json") as f:
    data = json.load(f)
    cluster_state = ClusterState.model_validate(data)

# Filter by namespace
namespace_resources = [
    r for r in cluster_state.resources 
    if r.metadata.namespace == "production"
]

# Find pod dependencies
for resource in namespace_resources:
    if resource.kind == "Pod":
        dependencies = resource.get_relationships_by_type(RelationshipType.USES)
        print(f"{resource.metadata.name} uses: {[d.target for d in dependencies]}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- Rich terminal UI powered by [Rich](https://rich.readthedocs.io/)
- Data validation with [Pydantic](https://pydantic.dev/)
- Package management with [uv](https://github.com/astral-sh/uv)
