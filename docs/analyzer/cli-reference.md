# 📋 k8s-analyzer CLI Reference

Complete command-line interface reference for the k8s-analyzer tool.

## Global Options

All commands support these global options:

```bash
--verbose, -v        Enable verbose logging
--help              Show help message and exit
--version           Show version information
```

## Commands Overview

| Command | Description |
|---------|-------------|
| `parse` | Parse kubectl export files and extract resources |
| `analyze` | Parse and analyze with relationship mapping |
| `report` | Generate comprehensive HTML analysis report |
| `graph` | Display resource relationship graph |
| `validate` | Validate resource configurations |
| `sqlite` | Export data to SQLite database |
| `csv` | Export data to CSV files |
| `scan` | Parse directory of files |
| `batch-analyze` | Full directory analysis |
| `export-multiple-sqlite` | Export multiple files to SQLite |
| `export-directory-sqlite` | Export entire directory to SQLite |
| `query-db` | Query existing SQLite database |
| `db-summary` | Database statistics |
| `export-csv` | Export database to CSV |

## Command Details

### `parse`

Parse kubectl export files and extract resources.

**Syntax:**
```bash
k8s-analyzer parse [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--additional, -a FILES` - Additional files to merge
- `--output, -o PATH` - Output file path (JSON format)
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Basic parsing
k8s-analyzer parse cluster-export.json

# Parse with additional files
k8s-analyzer parse main.json -a pods.json services.json

# Parse and save output
k8s-analyzer parse cluster-export.yaml -o parsed-resources.json
```

### `analyze`

Parse and analyze kubectl exports with relationship mapping.

**Syntax:**
```bash
k8s-analyzer analyze [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--additional, -a FILES` - Additional files to merge
- `--output, -o PATH` - Output file path (JSON format)
- `--namespace, -n NAMESPACE` - Filter by namespace
- `--include-kinds KINDS` - Include only specified resource kinds
- `--exclude-kinds KINDS` - Exclude specified resource kinds
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Full cluster analysis
k8s-analyzer analyze cluster-export.json

# Analyze specific namespace
k8s-analyzer analyze cluster-export.json -n production

# Analyze with kind filtering
k8s-analyzer analyze cluster-export.json --include-kinds Pod,Service,Deployment

# Save analysis results
k8s-analyzer analyze cluster-export.json -o analysis-results.json
```

### `report`

Generate comprehensive HTML analysis report.

**Syntax:**
```bash
k8s-analyzer report [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--additional, -a FILES` - Additional files to merge
- `--output, -o PATH` - Output HTML report path (default: cluster-report.html)
- `--template TEMPLATE` - Custom report template
- `--include-graphs` - Include relationship graphs in report
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Generate basic report
k8s-analyzer report cluster-export.json

# Custom output location
k8s-analyzer report cluster-export.json -o reports/cluster-analysis.html

# Report with graphs
k8s-analyzer report cluster-export.json --include-graphs
```

### `graph`

Display resource relationship graph.

**Syntax:**
```bash
k8s-analyzer graph [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--additional, -a FILES` - Additional files to merge
- `--namespace, -n NAMESPACE` - Filter by namespace
- `--type, -t TYPE` - Filter by resource type
- `--output-format FORMAT` - Output format (text, dot, svg)
- `--max-depth DEPTH` - Maximum relationship depth
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Display relationship graph
k8s-analyzer graph cluster-export.json

# Filter by namespace
k8s-analyzer graph cluster-export.json -n default

# Filter by resource type
k8s-analyzer graph cluster-export.json -t Pod

# Export as DOT format
k8s-analyzer graph cluster-export.json --output-format dot > graph.dot
```

### `validate`

Validate resource configurations and identify issues.

**Syntax:**
```bash
k8s-analyzer validate [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--additional, -a FILES` - Additional files to merge
- `--rules-file FILE` - Custom validation rules file
- `--severity LEVEL` - Minimum severity level (info, warning, error)
- `--output-format FORMAT` - Output format (text, json, yaml)
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Basic validation
k8s-analyzer validate cluster-export.json

# Show only errors
k8s-analyzer validate cluster-export.json --severity error

# Output as JSON
k8s-analyzer validate cluster-export.json --output-format json
```

### `sqlite`

Export data to SQLite database.

**Syntax:**
```bash
k8s-analyzer sqlite [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--output, -o DATABASE` - Output SQLite database path
- `--replace-existing` - Replace existing database
- `--batch-size SIZE` - Batch processing size (default: 100)
- `--include-relationships` - Include relationship analysis
- `--compress` - Compress database
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Export to SQLite
k8s-analyzer sqlite cluster-export.json --output cluster.db

# Replace existing database
k8s-analyzer sqlite cluster-export.json -o cluster.db --replace-existing

# Custom batch size for large clusters
k8s-analyzer sqlite large-cluster.json -o large.db --batch-size 50
```

### `csv`

Export data to CSV files.

**Syntax:**
```bash
k8s-analyzer csv [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to kubectl export file (JSON/YAML)

**Options:**
- `--output-dir, -o DIRECTORY` - Output directory for CSV files
- `--separate-files` - Create separate files per resource type
- `--include-relationships` - Include relationships CSV
- `--flatten-spec` - Flatten spec fields into columns
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Export to CSV directory
k8s-analyzer csv cluster-export.json --output-dir ./csv-reports

# Separate files per resource type
k8s-analyzer csv cluster-export.json -o ./reports --separate-files

# Include relationships
k8s-analyzer csv cluster-export.json -o ./reports --include-relationships
```

### `scan`

Parse directory of Kubernetes files.

**Syntax:**
```bash
k8s-analyzer scan [OPTIONS] DIRECTORY
```

**Arguments:**
- `DIRECTORY` - Directory containing Kubernetes files

**Options:**
- `--recursive, -r` - Scan subdirectories recursively
- `--pattern PATTERN` - File pattern to match (default: *.yaml,*.yml,*.json)
- `--output, -o PATH` - Output file path
- `--exclude-dirs DIRS` - Directories to exclude
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Scan directory
k8s-analyzer scan ./manifests

# Recursive scan
k8s-analyzer scan ./k8s-configs --recursive

# Custom pattern
k8s-analyzer scan ./configs --pattern "*.yaml"

# Exclude directories
k8s-analyzer scan ./all-configs --exclude-dirs .git,node_modules
```

### `batch-analyze`

Full directory analysis with relationships.

**Syntax:**
```bash
k8s-analyzer batch-analyze [OPTIONS] DIRECTORY
```

**Arguments:**
- `DIRECTORY` - Directory containing Kubernetes files

**Options:**
- `--recursive, -r` - Scan subdirectories recursively
- `--output, -o PATH` - Output analysis file
- `--parallel-jobs JOBS` - Number of parallel processing jobs
- `--chunk-size SIZE` - Files per processing chunk
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Batch analyze directory
k8s-analyzer batch-analyze ./manifests --output batch-results.json

# Parallel processing
k8s-analyzer batch-analyze ./large-configs --parallel-jobs 4

# Custom chunk size
k8s-analyzer batch-analyze ./configs --chunk-size 10
```

### `export-multiple-sqlite`

Export multiple files to SQLite database.

**Syntax:**
```bash
k8s-analyzer export-multiple-sqlite [OPTIONS] FILES...
```

**Arguments:**
- `FILES...` - Multiple kubectl export files

**Options:**
- `--database, -d DATABASE` - Output SQLite database path
- `--replace-existing` - Replace existing database
- `--batch-size SIZE` - Batch processing size
- `--merge-strategy STRATEGY` - How to handle conflicts (merge, replace, skip)
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Export multiple files
k8s-analyzer export-multiple-sqlite file1.json file2.yaml -d combined.db

# Replace existing database
k8s-analyzer export-multiple-sqlite *.json -d cluster.db --replace-existing

# Custom merge strategy
k8s-analyzer export-multiple-sqlite cluster1.json cluster2.json \
  -d multi-cluster.db --merge-strategy merge
```

### `export-directory-sqlite`

Export entire directory to SQLite database.

**Syntax:**
```bash
k8s-analyzer export-directory-sqlite [OPTIONS] DIRECTORY DATABASE
```

**Arguments:**
- `DIRECTORY` - Directory containing Kubernetes files
- `DATABASE` - Output SQLite database path

**Options:**
- `--recursive, -r` - Process subdirectories recursively
- `--pattern PATTERN` - File pattern to match
- `--batch-size SIZE` - Batch processing size
- `--replace-existing` - Replace existing database
- `--exclude-dirs DIRS` - Directories to exclude
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Export directory to SQLite
k8s-analyzer export-directory-sqlite ./manifests cluster.db

# Recursive with custom pattern
k8s-analyzer export-directory-sqlite ./configs cluster.db \
  --recursive --pattern "*.yaml"

# Large directory with batching
k8s-analyzer export-directory-sqlite ./large-cluster cluster.db \
  --batch-size 50 --replace-existing
```

### `query-db`

Query existing SQLite database.

**Syntax:**
```bash
k8s-analyzer query-db [OPTIONS] DATABASE
```

**Arguments:**
- `DATABASE` - Path to SQLite database

**Options:**
- `--sql QUERY` - SQL query to execute
- `--kind KIND` - Filter by resource kind
- `--namespace NAMESPACE` - Filter by namespace
- `--health-status STATUS` - Filter by health status
- `--output-format FORMAT` - Output format (table, json, csv)
- `--limit LIMIT` - Limit number of results
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Query by resource kind
k8s-analyzer query-db cluster.db --kind Pod

# Query by namespace
k8s-analyzer query-db cluster.db --namespace production

# Custom SQL query
k8s-analyzer query-db cluster.db --sql "SELECT * FROM resources WHERE kind='Service'"

# Output as JSON
k8s-analyzer query-db cluster.db --kind ConfigMap --output-format json
```

### `db-summary`

Get database statistics and summary.

**Syntax:**
```bash
k8s-analyzer db-summary [OPTIONS] DATABASE
```

**Arguments:**
- `DATABASE` - Path to SQLite database

**Options:**
- `--detailed` - Show detailed statistics
- `--output-format FORMAT` - Output format (table, json, yaml)
- `--include-schema` - Include database schema information
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Basic summary
k8s-analyzer db-summary cluster.db

# Detailed statistics
k8s-analyzer db-summary cluster.db --detailed

# JSON output
k8s-analyzer db-summary cluster.db --output-format json

# Include schema
k8s-analyzer db-summary cluster.db --include-schema
```

### `export-csv`

Export SQLite database to CSV files.

**Syntax:**
```bash
k8s-analyzer export-csv [OPTIONS] DATABASE DIRECTORY
```

**Arguments:**
- `DATABASE` - Path to SQLite database
- `DIRECTORY` - Output directory for CSV files

**Options:**
- `--tables TABLES` - Specific tables to export (comma-separated)
- `--include-relationships` - Include relationships table
- `--flatten-json` - Flatten JSON columns
- `--delimiter DELIMITER` - CSV delimiter (default: comma)
- `--verbose, -v` - Enable verbose logging

**Examples:**
```bash
# Export all tables
k8s-analyzer export-csv cluster.db ./csv-export

# Export specific tables
k8s-analyzer export-csv cluster.db ./exports --tables resources,relationships

# Custom delimiter
k8s-analyzer export-csv cluster.db ./exports --delimiter ";"

# Flatten JSON columns
k8s-analyzer export-csv cluster.db ./exports --flatten-json
```

## Environment Variables

Configure k8s-analyzer behavior using environment variables:

```bash
# Output configuration
export K8S_ANALYZER_OUTPUT_DIR="./analysis"
export K8S_ANALYZER_LOG_LEVEL="INFO"

# Performance tuning
export K8S_ANALYZER_BATCH_SIZE="100"
export K8S_ANALYZER_PARALLEL_JOBS="4"

# Database configuration
export K8S_ANALYZER_DB_TIMEOUT="30"
export K8S_ANALYZER_DB_PRAGMA="journal_mode=WAL"
```

## Exit Codes

k8s-analyzer uses the following exit codes:

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Parse error
- `5` - Database error
- `6` - Permission error

## Performance Tips

### Large Clusters
```bash
# Use batch processing
k8s-analyzer sqlite large-cluster.json -o large.db --batch-size 50

# Parallel processing for directories
k8s-analyzer batch-analyze ./configs --parallel-jobs 4
```

### Memory Optimization
```bash
# Process files individually
k8s-analyzer sqlite pods.json -o pods.db
k8s-analyzer sqlite services.json -o services.db

# Use streaming for very large files
k8s-analyzer parse huge-cluster.json --stream-processing
```

### Database Optimization
```bash
# Enable compression
k8s-analyzer sqlite cluster.json -o cluster.db --compress

# Optimize database after creation
sqlite3 cluster.db "VACUUM; ANALYZE;"
```

## Common Patterns

### Daily Cluster Analysis
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
kubectl get all,pv,pvc,configmaps,secrets -A -o json > "cluster-${DATE}.json"
k8s-analyzer sqlite "cluster-${DATE}.json" -o "analysis-${DATE}.db" --replace-existing
k8s-analyzer report "cluster-${DATE}.json" -o "report-${DATE}.html"
```

### Multi-Environment Analysis
```bash
# Analyze multiple environments
k8s-analyzer export-multiple-sqlite \
  dev-cluster.json staging-cluster.json prod-cluster.json \
  -d multi-env.db --replace-existing

# Generate comparative report
k8s-analyzer query-db multi-env.db --sql "
  SELECT namespace, kind, COUNT(*) as count 
  FROM resources 
  GROUP BY namespace, kind 
  ORDER BY namespace, count DESC"
```

### Continuous Integration
```bash
# In CI pipeline
k8s-analyzer validate manifests/ --severity error --output-format json > validation-results.json
if [ $? -ne 0 ]; then
  echo "Validation failed"
  exit 1
fi
```

## Troubleshooting

### Common Issues

**File Not Found:**
```bash
# Check file exists and is readable
ls -la cluster-export.json
file cluster-export.json
```

**Parse Errors:**
```bash
# Validate JSON/YAML syntax
jq . cluster-export.json > /dev/null
yamllint cluster-export.yaml
```

**Database Errors:**
```bash
# Check database integrity
sqlite3 cluster.db "PRAGMA integrity_check;"

# Repair database if needed
sqlite3 cluster.db "VACUUM;"
```

**Memory Issues:**
```bash
# Use smaller batch sizes
k8s-analyzer sqlite large-cluster.json -o large.db --batch-size 25

# Monitor memory usage
time k8s-analyzer analyze cluster.json
```

For more troubleshooting help, see the [Troubleshooting Guide](../reference/troubleshooting.md).
