# 🗒️ CLI Commands Reference

This document provides a comprehensive reference for all CLI commands available in the k8s-tools suite, offering detailed information on their usage, options, arguments, and practical examples.

## k8s-analyzer Commands

### `analyzer analyze`
Analyzes the current state of the Kubernetes cluster or provided YAML files.

```bash
k8s-analyzer analyze [OPTIONS]
```

**Options:**
- `--output`: Path to output file where analysis result will be stored.
- `--stdin`: Read input from standard input.
- `--verbose`: Enable verbose output for detailed analysis logs.

**Examples:**
- Analyze current cluster: `k8s-analyzer analyze`
- Analyze and export results: `k8s-analyzer analyze --output analysis.json`

### `analyzer report`
Generates a report from analysis data in various formats.

```bash
k8s-analyzer report [SOURCE] [OPTIONS]
```

**Options:**
- `--format`: Output format (html, json, csv).
- `--output`: Path to output report file.
- `--title`: Title for the generated report.

**Examples:**
- Generate HTML report: `k8s-analyzer report analysis.json --format html --output report.html`

## k8s-reporter Commands

### `reporter start`
Starts the k8s-reporter dashboard service.

```bash
k8s-reporter start [OPTIONS]
```

**Options:**
- `--config`: Path to configuration file.

**Examples:**
- Start service with config: `k8s-reporter start --config config.yaml`

### `reporter generate`
Generates reports based on the specified schedule and configuration.

```bash
k8s-reporter generate [OPTIONS]
```

**Options:**
- `--format`: Output format (html, pdf).
- `--output`: Path to output report directory.

**Examples:**
- Generate HTML report: `k8s-reporter generate --format html --output reports/`

## General Options

- `--help`: Show help information for any command.

## Advanced Usage

### Using with Continuous Integration
Integrate CLI commands in CI pipelines for automated analysis and reporting.

**Example with GitHub Actions:**
```yaml
jobs:
  analyze:
    steps:
      - run: k8s-analyzer analyze --output analysis.json
      - run: k8s-analyzer report analysis.json --format html --output report.html
```

### Custom Script Integration
Utilize CLI commands in scripts to automate routine tasks.

**Example Script:**
```bash
#!/bin/bash
# Automate analysis and reporting
date=$(date +%Y%m%d)

k8s-analyzer analyze --output analysis-${date}.json
k8s-analyzer report analysis-${date}.json --format html --output reports/${date}-report.html
```

This CLI reference enables users to effectively utilize k8s-tools commands, enhancing productivity and integration into various environments.
