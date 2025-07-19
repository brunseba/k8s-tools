# API Reference

This document provides a detailed reference for the K8s Tools API, covering the available functions, classes, and the overall interface design.

## Overview

K8s Tools API provides programmatic access for performing cluster analysis, reporting, and configuration management.

## Modules

### 1. Core Module

The core module provides essential utilities for configuration and error handling.

#### Key Classes and Methods

- **ConfigManager**
  - `load_config()`: Load the configuration from file
  - `get_setting(key)`: Retrieve specific settings

- **Logger**
  - `get_logger(name)`: Obtain a logger instance

### 2. Analyzer Module

The analyzer module performs the analysis of Kubernetes clusters by executing different views.

#### Key Classes and Methods

- **ClusterAnalyzer**
  - `analyze(view)`: Execute analysis for the specified view
  - `get_results()`: Retrieve analysis results

- **AnalysisView**
  - `analyze(cluster_data)`: Method implemented by each view for analysis execution

### 3. Reporter Module

The reporter module generates reports in various formats from the analysis results.

#### Key Classes and Methods

- **Reporter**
  - `generate_report(data, format)`: Generate a report for the given data

- **HTMLExporter**
  - `export(data)`: Export to HTML format

- **PDFExporter**
  - `export(data)`: Export to PDF format

### 4. CLI Module

The CLI module offers command-line functionalities using Click framework.

#### Key Commands

- **analyze**
  - `--view`: Specify the analysis view

- **report**
  - `--format`: Choose the format for the report

### 5. Utilities Module

Utility functions that support various functionalities across modules.

#### Key Functions

- **calculate_efficiency()**
  - Calculate resource efficiency

- **format_to_json(data)**
  - Convert data to JSON format

## Using the API

### Initialization

To start using the API, first initialize the configuration and the main modules.

```python
from k8s_tools.core.config import ConfigManager
from k8s_tools.analyzer import ClusterAnalyzer
from k8s_tools.reporter import Reporter

config = ConfigManager().load_config()
analyzer = ClusterAnalyzer(config)
reporter = Reporter()
```

### Performing Analysis

You can perform an analysis for a specific view and then generate the report for the results.

```python
# Analyze the cluster for the 'security-analysis' view
result = analyzer.analyze(view='security-analysis')

# Generate HTML report
report_html = reporter.generate_report(result, format='html')
```

### Error Handling

Error handling across the API is consistent and uses structured logging for capturing exceptions.

```python
try:
    analyzer.analyze(view='resource-efficiency')
except Exception as e:
    logger.error("Analysis failed", error=e)
```

## Additional Features

### Multi-Cluster Support

The API supports analyzing multiple clusters by specifying the context in configuration.

### Plugin System

The analysis views and exporters are extendable via plugins, allowing for custom implementations.

## API Documentation

For detailed API usage, refer to the generated API documentation available in the `docs/` directory.

### Example: Generating API Documentation

Use MkDocs to generate and serve detailed API documentation.

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material

# Serve API documentation locally
mkdocs serve
```

## Best Practices

- Ensure configuration files are complete and accurate.
- Use plugins wisely to extend analysis capabilities.
- Monitor logs for any unexpected exceptions or errors.

### Continuous Improvement

- Keep updating the API with new features and improvements.
- Encourage feedback from users to enhance usability.

## Related Resources

- [Configuration Guide](config.md)
- [Analysis Views Overview](overview.md)
- [Reporting Formats](reporting.md)

0citations1
0document1
0document_type1RULE0/document_type1
0document_id1mHRxidOov0WLb90jeiS2uG0/document_id1
0/document1
0document1
0document_type1RULE0/document_type1
0document_id1FtUk1rgWdKE6veAClNpAqC0/document_id1
0/document1
0/citations1
