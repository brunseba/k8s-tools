# Multi-cluster Analysis

This guide covers analyzing multiple Kubernetes clusters using k8s-analyzer and k8s-reporter, focusing on processing multiple cluster exports and consolidating results.

## Overview

Multi-cluster analysis with K8s Tools enables:

- **Batch Processing**: Analyze exports from multiple clusters
- **Comparative Analysis**: Compare resource states across different clusters
- **Consolidated Storage**: Store all cluster data in unified SQLite databases
- **Cross-cluster Reporting**: Generate reports across multiple cluster states

## Prerequisites

### Exporting Cluster Data

First, export data from each cluster you want to analyze:

```bash
# Export from production cluster
kubectl --context=production get all --all-namespaces -o yaml > production-export.yaml

# Export from staging cluster
kubectl --context=staging get all --all-namespaces -o yaml > staging-export.yaml

# Export from development cluster
kubectl --context=development get all --all-namespaces -o yaml > development-export.yaml
```

### Directory Structure

Organize cluster exports in a structured directory:

```
multi-cluster-analysis/
├── exports/
│   ├── production/
│   │   ├── cluster-export.yaml
│   │   └── additional-resources.yaml
│   ├── staging/
│   │   └── cluster-export.yaml
│   └── development/
│       └── cluster-export.yaml
├── results/
│   ├── production/
│   ├── staging/
│   └── development/
└── consolidated/
    ├── all-clusters.db
    └── comparison-report.html
```

## Running Multi-cluster Analysis

### Sequential Analysis

Analyze each cluster export individually:

```bash
# Analyze production cluster
k8s-analyzer analyze exports/production/cluster-export.yaml \
  --output results/production/analysis.json

# Analyze staging cluster
k8s-analyzer analyze exports/staging/cluster-export.yaml \
  --output results/staging/analysis.json

# Analyze development cluster
k8s-analyzer analyze exports/development/cluster-export.yaml \
  --output results/development/analysis.json
```

### Parallel Analysis Script

Process multiple clusters simultaneously:

```bash
#!/bin/bash
# multi-cluster-analysis.sh

CLUSTERS=("production" "staging" "development")
EXPORT_DIR="exports"
RESULT_DIR="results"

mkdir -p "$RESULT_DIR"

# Function to analyze a single cluster
analyze_cluster() {
    local cluster=$1
    local export_file="$EXPORT_DIR/$cluster/cluster-export.yaml"
    local result_dir="$RESULT_DIR/$cluster"
    
    echo "[$(date)] Starting analysis for $cluster..."
    
    if [ ! -f "$export_file" ]; then
        echo "Warning: Export file not found for $cluster: $export_file"
        return 1
    fi
    
    mkdir -p "$result_dir"
    
    # Analyze the cluster export
    k8s-analyzer analyze "$export_file" \
        --output "$result_dir/analysis.json" \
        --verbose
    
    # Generate HTML report
    k8s-analyzer report "$export_file" \
        --output "$result_dir/report.html"
    
    # Export to SQLite
    k8s-analyzer export-sqlite "$export_file" \
        "$result_dir/cluster.db"
    
    # Generate validation report
    k8s-analyzer validate "$export_file" > "$result_dir/validation.txt" 2>&1
    
    echo "[$(date)] Completed analysis for $cluster"
}

# Run analysis for each cluster in parallel
for cluster in "${CLUSTERS[@]}"; do
    analyze_cluster "$cluster" &
done

# Wait for all background jobs to complete
wait

echo "[$(date)] All cluster analyses completed!"
```

### Batch Processing with Multiple Files

Use k8s-analyzer's batch capabilities:

```bash
#!/bin/bash
# batch-multi-cluster.sh

# Process all cluster exports in one batch
k8s-analyzer export-multiple-sqlite \
    exports/production/cluster-export.yaml \
    exports/staging/cluster-export.yaml \
    exports/development/cluster-export.yaml \
    --database consolidated/all-clusters.db \
    --batch-size 5 \
    --verbose

echo "All clusters exported to consolidated database"
```

### Using Make for Orchestration

```makefile
# Makefile for multi-cluster analysis
.PHONY: analyze-all export-all consolidate clean

EXPORT_DIR = exports
RESULT_DIR = results
CONSOLIDATED_DIR = consolidated

CLUSTERS = production staging development

analyze-all: $(addprefix analyze-, $(CLUSTERS))

analyze-%:
	@echo "Analyzing cluster: $*"
	@mkdir -p $(RESULT_DIR)/$*
	k8s-analyzer analyze $(EXPORT_DIR)/$*/cluster-export.yaml \
		--output $(RESULT_DIR)/$*/analysis.json
	k8s-analyzer report $(EXPORT_DIR)/$*/cluster-export.yaml \
		--output $(RESULT_DIR)/$*/report.html
	k8s-analyzer export-sqlite $(EXPORT_DIR)/$*/cluster-export.yaml \
		$(RESULT_DIR)/$*/cluster.db

export-all: analyze-all
	@echo "Consolidating all cluster databases..."
	@mkdir -p $(CONSOLIDATED_DIR)
	k8s-analyzer export-multiple-sqlite \
		$(wildcard $(RESULT_DIR)/*/cluster.db) \
		--database $(CONSOLIDATED_DIR)/all-clusters.db

consolidate: export-all
	@echo "Generating consolidated reports..."
	k8s-analyzer db-summary $(CONSOLIDATED_DIR)/all-clusters.db \
		> $(CONSOLIDATED_DIR)/summary.txt
	k8s-analyzer query-db $(CONSOLIDATED_DIR)/all-clusters.db \
		--issues > $(CONSOLIDATED_DIR)/issues-report.txt
	k8s-analyzer export-csv $(CONSOLIDATED_DIR)/all-clusters.db \
		$(CONSOLIDATED_DIR)/csv-exports/

clean:
	rm -rf $(RESULT_DIR)/* $(CONSOLIDATED_DIR)/*
```

## Consolidated Reporting and Analysis

### Database Consolidation

Combine multiple cluster databases for unified analysis:

```bash
#!/bin/bash
# consolidate-clusters.sh

CONSOLIDATED_DB="consolidated/all-clusters.db"
mkdir -p consolidated

# Export all cluster data to a single consolidated database
k8s-analyzer export-multiple-sqlite \
    results/production/cluster.db \
    results/staging/cluster.db \
    results/development/cluster.db \
    --database "$CONSOLIDATED_DB" \
    --batch-size 10

echo "Consolidated database created: $CONSOLIDATED_DB"
```

### Cross-cluster Analysis

Analyze patterns across all clusters:

```bash
#!/bin/bash
# cross-cluster-analysis.sh

DB="consolidated/all-clusters.db"
REPORT_DIR="consolidated/reports"

mkdir -p "$REPORT_DIR"

echo "=== Multi-Cluster Analysis Report ===" > "$REPORT_DIR/analysis.txt"
echo "Generated: $(date)" >> "$REPORT_DIR/analysis.txt"
echo "" >> "$REPORT_DIR/analysis.txt"

# Overall statistics
echo "=== OVERALL STATISTICS ===" >> "$REPORT_DIR/analysis.txt"
k8s-analyzer db-summary "$DB" >> "$REPORT_DIR/analysis.txt"
echo "" >> "$REPORT_DIR/analysis.txt"

# Resources with issues across all clusters
echo "=== CROSS-CLUSTER ISSUES ===" >> "$REPORT_DIR/analysis.txt"
k8s-analyzer query-db "$DB" --issues --limit 100 >> "$REPORT_DIR/analysis.txt"
echo "" >> "$REPORT_DIR/analysis.txt"

# Export to CSV for detailed analysis
echo "Exporting to CSV..."
k8s-analyzer export-csv "$DB" "$REPORT_DIR/csv/"

echo "Cross-cluster analysis complete: $REPORT_DIR"
```

## Dashboard Integration with k8s-reporter

### Multi-cluster Dashboard

Launch k8s-reporter with consolidated database:

```bash
#!/bin/bash
# launch-multi-cluster-dashboard.sh

CONSOLIDATED_DB="consolidated/all-clusters.db"
PORT="8080"
HOST="0.0.0.0"

# Ensure consolidated database exists
if [ ! -f "$CONSOLIDATED_DB" ]; then
    echo "Error: Consolidated database not found: $CONSOLIDATED_DB"
    echo "Run consolidation script first"
    exit 1
fi

echo "Starting multi-cluster dashboard..."
echo "Database: $CONSOLIDATED_DB"
echo "URL: http://$HOST:$PORT"
echo ""

# Start k8s-reporter with consolidated data
k8s-reporter \
    --database "$CONSOLIDATED_DB" \
    --host "$HOST" \
    --port "$PORT" \
    --headless
```

### Automated Multi-cluster Pipeline

Complete end-to-end automation:

```bash
#!/bin/bash
# complete-multi-cluster-pipeline.sh

set -e  # Exit on any error

CLUSTERS=("production" "staging" "development")
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
WORK_DIR="multi-cluster-$TIMESTAMP"
CONSOLIDATED_DB="$WORK_DIR/all-clusters.db"

echo "Starting multi-cluster analysis pipeline..."
echo "Working directory: $WORK_DIR"

# Step 1: Create working directory
mkdir -p "$WORK_DIR"/{exports,results,consolidated}

# Step 2: Export cluster data (assuming kubectl contexts are configured)
echo "Exporting cluster data..."
for cluster in "${CLUSTERS[@]}"; do
    echo "Exporting $cluster cluster..."
    kubectl --context="$cluster" get all --all-namespaces -o yaml > \
        "$WORK_DIR/exports/$cluster-export.yaml"
done

# Step 3: Analyze each cluster
echo "Analyzing clusters..."
for cluster in "${CLUSTERS[@]}"; do
    export_file="$WORK_DIR/exports/$cluster-export.yaml"
    result_dir="$WORK_DIR/results/$cluster"
    
    mkdir -p "$result_dir"
    
    echo "Analyzing $cluster..."
    k8s-analyzer analyze "$export_file" \
        --output "$result_dir/analysis.json"
    
    k8s-analyzer export-sqlite "$export_file" \
        "$result_dir/cluster.db"
    
    k8s-analyzer report "$export_file" \
        --output "$result_dir/report.html"
done

# Step 4: Consolidate results
echo "Consolidating results..."
k8s-analyzer export-multiple-sqlite \
    "$WORK_DIR"/results/*/cluster.db \
    --database "$CONSOLIDATED_DB"

# Step 5: Generate consolidated reports
echo "Generating consolidated reports..."
k8s-analyzer db-summary "$CONSOLIDATED_DB" > \
    "$WORK_DIR/consolidated/summary.txt"

k8s-analyzer query-db "$CONSOLIDATED_DB" --issues > \
    "$WORK_DIR/consolidated/issues.txt"

k8s-analyzer export-csv "$CONSOLIDATED_DB" \
    "$WORK_DIR/consolidated/csv/"

# Step 6: Launch dashboard
echo "Launching dashboard..."
echo "Results available in: $WORK_DIR"
echo "Dashboard URL: http://localhost:8080"

k8s-reporter \
    --database "$CONSOLIDATED_DB" \
    --port 8080 \
    --host 0.0.0.0
```

## Best Practices

### Security Considerations

1. **Kubeconfig Management**: Store kubeconfigs securely
2. **Access Controls**: Use least-privilege access for analysis
3. **Network Segmentation**: Ensure proper network isolation between clusters

### Performance Optimization

1. **Parallel Processing**: Run cluster analyses in parallel
2. **Resource Limits**: Set appropriate resource limits for analysis containers
3. **Caching**: Cache results to avoid redundant analyses

### Operational Guidelines

1. **Standardization**: Use consistent naming conventions across clusters
2. **Automation**: Automate analysis scheduling and reporting
3. **Monitoring**: Set up alerts for analysis failures or anomalies

## Troubleshooting

### Common Issues

#### Kubeconfig Access Errors
```bash
# Test kubeconfig access
kubectl --kubeconfig ~/.kube/prod-config cluster-info
```

#### Resource Conflicts
```bash
# Check resource availability before analysis
kubectl --kubeconfig ~/.kube/prod-config top nodes
```

### Debugging Multi-cluster Issues

```bash
# Enable verbose logging
k8s-analyzer analyze --verbose --config multi-cluster-config.yaml

# Test individual cluster connectivity
k8s-analyzer test-connection --cluster production
```

## Related Documentation

- [Basic Usage](basic-usage.md)
- [Advanced Workflows](advanced-workflows.md)
- [CI/CD Integration](../deployment/cicd.md)
- [Docker Deployment](../deployment/docker.md)

<citations>
<document>
<document_type>RULE</document_type>
<document_id>9aelDXM62tUDmHUQUL8XlE</document_id>
</document>
<document>
<document_type>RULE</document_type>
<document_id>VtweVW31OVFWgQwKe1SXqm</document_id>
</document>
</citations>
