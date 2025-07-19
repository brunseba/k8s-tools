# Custom Dashboards [ongoing]
This guide shows how to use k8s-reporter's Streamlit-based web dashboard for visualizing Kubernetes cluster analysis data from k8s-analyzer.

## Overview

k8s-reporter provides:

- **Interactive Web UI**: Streamlit-based dashboard for exploring analysis results
- **Database Integration**: Direct connection to SQLite databases from k8s-analyzer
- **Multiple Views**: Various visualization options for different data aspects
- **Export Capabilities**: Download results and generate reports

## Getting Started with k8s-reporter

### Basic Dashboard Launch

Start the web dashboard with a pre-analyzed database:

```bash
# First, create a database with k8s-analyzer
k8s-analyzer export-sqlite cluster-export.yaml cluster.db

# Launch k8s-reporter dashboard
k8s-reporter --database cluster.db
```

The dashboard will be available at `http://localhost:8501` by default.

### Custom Configuration

Launch with custom settings:

```bash
# Custom port and host
k8s-reporter --database cluster.db --port 8080 --host 0.0.0.0

# Headless mode (no auto-open browser)
k8s-reporter --database cluster.db --headless

# Debug mode for development
k8s-reporter --database cluster.db --debug
```

## Extending with Plugins

### Developing Plugins

Write plugins to capture specific cluster views and data:

```python
from k8s_tools.plugins import PluginBase

class MyDashboardPlugin(PluginBase):
    def register(self, registry):
        registry.add_view('custom-view', self.custom_view)

    def custom_view(self):
        # Implement custom data logic
        return "Custom View Results"
```

### Deploying Plugins

Include plugins in the K8s Tools configuration:

```yaml
# plugins.yaml
plugins:
  - path: /path/to/plugin1.py
  - path: /path/to/plugin2.py
```

Activate plugins with K8s Tools:

```bash
k8s-analyzer analyze --config my-config.yaml --plugins plugins.yaml
```

## Performance Optimization

1. **Optimize Queries**: Efficient query design enhances performance
2. **Cache Results**: Save query results to reduce load
3. **Separate Environments**: Run custom dashboards in non-production environments

## Security Considerations

- **Access Control**: Manage user access to dashboards
- **Data Protection**: Encrypt sensitive data

## Troubleshooting

### Common Issues

**Data Mismatch**: Ensure the data source aligns with dashboard expectations.
**Plugin Load Errors**: Validate plugin paths and configurations.

## Best Practices

1. **Iterative Testing**: Incremental dashboard testing ensures accuracy
2. **Community Templates**: Leverage community templates for common use cases

## FAQ

**Q**: How do I reset a panel?
**A**: Use the "Edit" function to restore default settings or adjust queries.

## Related Documentation

- [Basic Usage](../examples/basic-usage.md)
- [Advanced Workflows](../examples/advanced-workflows.md)
- [CI/CD Integration](../deployment/cicd.md)
