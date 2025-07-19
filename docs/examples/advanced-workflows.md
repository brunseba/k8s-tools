# Advanced Workflows

This document outlines advanced workflows and automation techniques using k8s-analyzer and k8s-reporter for complex Kubernetes analysis scenarios.

## Overview

Advanced K8s Tools workflows support:

- **Automated Analysis Pipelines**: Scripted analysis workflows
- **Database Integration**: SQLite-based persistent storage
- **Batch Processing**: Large-scale file processing
- **Custom Reporting**: Automated report generation
- **CI/CD Integration**: Pipeline automation

## Advanced k8s-analyzer Workflows

### Multi-File Processing Pipeline

Process and analyze multiple Kubernetes export files systematically:

```bash
#!/bin/bash
# Advanced multi-file analysis pipeline

SRC_DIR="./cluster-exports"
OUT_DIR="./analysis-results/$(date +%Y-%m-%d-%H%M%S)"
DB_FILE="$OUT_DIR/consolidated.db"

mkdir -p "$OUT_DIR"

# Step 1: Batch analyze all files in directory
echo "Starting batch analysis..."
k8s-analyzer batch-analyze "$SRC_DIR" \
    --recursive \
    --max-files 100 \
    --output "$OUT_DIR/batch-analysis.json" \
    --verbose

# Step 2: Export to SQLite for querying
echo "Exporting to SQLite database..."
k8s-analyzer export-directory-sqlite "$SRC_DIR" "$DB_FILE" \
    --recursive \
    --max-files 100

# Step 3: Generate summary statistics
echo "Generating database summary..."
k8s-analyzer db-summary "$DB_FILE" > "$OUT_DIR/summary.txt"

# Step 4: Query for problematic resources
echo "Identifying issues..."
k8s-analyzer query-db "$DB_FILE" \
    --issues \
    --limit 50 > "$OUT_DIR/issues-report.txt"

# Step 5: Export to CSV for spreadsheet analysis
echo "Exporting to CSV..."
k8s-analyzer export-csv "$DB_FILE" "$OUT_DIR/csv-exports/"

echo "Analysis pipeline complete. Results in: $OUT_DIR"
```

### Resource Health Monitoring Script

Automated script for monitoring resource health across multiple exports:

```bash
#!/bin/bash
# Resource health monitoring and alerting

DB_PATH="$1"
ALERT_THRESHOLD="10"  # Alert if more than 10 resources have issues

if [ -z "$DB_PATH" ]; then
    echo "Usage: $0 <database-path>"
    exit 1
fi

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "Database not found: $DB_PATH"
    exit 1
fi

# Query for resources with issues
ISSUE_COUNT=$(k8s-analyzer query-db "$DB_PATH" --issues --limit 1000 | grep -c "^|")
ISSUE_COUNT=$((ISSUE_COUNT - 1))  # Subtract header row

echo "Found $ISSUE_COUNT resources with issues"

# Generate detailed report if issues found
if [ "$ISSUE_COUNT" -gt 0 ]; then
    REPORT_FILE="health-report-$(date +%Y%m%d-%H%M%S).txt"
    
    echo "Generating detailed health report: $REPORT_FILE"
    {
        echo "=== Kubernetes Cluster Health Report ==="
        echo "Generated: $(date)"
        echo "Database: $DB_PATH"
        echo "Total Issues Found: $ISSUE_COUNT"
        echo ""
        
        echo "=== Resources with Issues ==="
        k8s-analyzer query-db "$DB_PATH" --issues --limit 100
        
        echo ""
        echo "=== Database Summary ==="
        k8s-analyzer db-summary "$DB_PATH"
        
    } > "$REPORT_FILE"
    
    # Alert if threshold exceeded
    if [ "$ISSUE_COUNT" -gt "$ALERT_THRESHOLD" ]; then
        echo "⚠️  ALERT: Issue count ($ISSUE_COUNT) exceeds threshold ($ALERT_THRESHOLD)"
        # Here you could send email, Slack notification, etc.
    fi
fi
```

### Comparative Analysis Workflow

Compare resource states across different time periods:

```bash
#!/bin/bash
# Comparative analysis between two cluster states

OLD_EXPORT="$1"
NEW_EXPORT="$2"
COMPARE_DIR="./comparison-$(date +%Y%m%d-%H%M%S)"

if [ -z "$OLD_EXPORT" ] || [ -z "$NEW_EXPORT" ]; then
    echo "Usage: $0 <old-export.yaml> <new-export.yaml>"
    exit 1
fi

mkdir -p "$COMPARE_DIR"

# Analyze both exports
echo "Analyzing old state..."
k8s-analyzer analyze "$OLD_EXPORT" --output "$COMPARE_DIR/old-analysis.json"
k8s-analyzer export-sqlite "$OLD_EXPORT" "$COMPARE_DIR/old-state.db"

echo "Analyzing new state..."
k8s-analyzer analyze "$NEW_EXPORT" --output "$COMPARE_DIR/new-analysis.json"
k8s-analyzer export-sqlite "$NEW_EXPORT" "$COMPARE_DIR/new-state.db"

# Generate comparison reports
echo "Generating comparison reports..."
{
    echo "=== Cluster State Comparison Report ==="
    echo "Generated: $(date)"
    echo "Old State: $OLD_EXPORT"
    echo "New State: $NEW_EXPORT"
    echo ""
    
    echo "=== OLD STATE SUMMARY ==="
    k8s-analyzer db-summary "$COMPARE_DIR/old-state.db"
    
    echo ""
    echo "=== NEW STATE SUMMARY ==="
    k8s-analyzer db-summary "$COMPARE_DIR/new-state.db"
    
    echo ""
    echo "=== ISSUES IN OLD STATE ==="
    k8s-analyzer query-db "$COMPARE_DIR/old-state.db" --issues
    
    echo ""
    echo "=== ISSUES IN NEW STATE ==="
    k8s-analyzer query-db "$COMPARE_DIR/new-state.db" --issues
    
} > "$COMPARE_DIR/comparison-report.txt"

echo "Comparison complete. Results in: $COMPARE_DIR"
```

## Advanced k8s-reporter Integration

### Automated Dashboard Deployment

Script to automatically deploy dashboards with pre-loaded data:

```bash
#!/bin/bash
# Deploy k8s-reporter dashboard with automated data loading

CLUSTER_EXPORT="$1"
PORT="${2:-8080}"
HOST="${3:-0.0.0.0}"

if [ -z "$CLUSTER_EXPORT" ]; then
    echo "Usage: $0 <cluster-export.yaml> [port] [host]"
    exit 1
fi

# Prepare data directory
DATA_DIR="./dashboard-data-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DATA_DIR"

echo "Preparing dashboard data..."

# Process cluster export
k8s-analyzer analyze "$CLUSTER_EXPORT" --output "$DATA_DIR/analysis.json"
k8s-analyzer export-sqlite "$CLUSTER_EXPORT" "$DATA_DIR/cluster.db"

# Generate static reports
k8s-analyzer report "$CLUSTER_EXPORT" --output "$DATA_DIR/cluster-report.html"

# Export CSV for additional analysis
k8s-analyzer export-csv "$DATA_DIR/cluster.db" "$DATA_DIR/csv-exports/"

echo "Starting k8s-reporter dashboard..."
echo "Dashboard will be available at: http://$HOST:$PORT"
echo "Database location: $DATA_DIR/cluster.db"
echo ""

# Start the dashboard
k8s-reporter \
    --host "$HOST" \
    --port "$PORT" \
    --database "$DATA_DIR/cluster.db" \
    --headless
```

### Production Dashboard Setup

Production-ready setup with monitoring and logging:

```bash
#!/bin/bash
# Production k8s-reporter setup with monitoring

PORT="8080"
LOG_DIR="./logs"
DATA_DIR="./data"
PID_FILE="./k8s-reporter.pid"

mkdir -p "$LOG_DIR" "$DATA_DIR"

# Function to start the dashboard
start_dashboard() {
    echo "Starting k8s-reporter in production mode..."
    
    nohup k8s-reporter \
        --host 0.0.0.0 \
        --port "$PORT" \
        --headless \
        --database "$DATA_DIR/cluster.db" \
        > "$LOG_DIR/k8s-reporter.log" 2>&1 &
    
    echo $! > "$PID_FILE"
    echo "k8s-reporter started with PID $(cat $PID_FILE)"
    echo "Logs: $LOG_DIR/k8s-reporter.log"
}

# Function to stop the dashboard
stop_dashboard() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Stopping k8s-reporter (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
    else
        echo "No PID file found. Dashboard may not be running."
    fi
}

# Function to check dashboard status
status_dashboard() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null; then
            echo "k8s-reporter is running (PID: $PID)"
            echo "Dashboard URL: http://localhost:$PORT"
        else
            echo "PID file exists but process is not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "k8s-reporter is not running"
    fi
}

# Handle command line arguments
case "$1" in
    start)
        start_dashboard
        ;;
    stop)
        stop_dashboard
        ;;
    restart)
        stop_dashboard
        sleep 2
        start_dashboard
        ;;
    status)
        status_dashboard
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

## CI/CD Pipeline Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/k8s-analysis.yml
name: Kubernetes Analysis Pipeline

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:
  push:
    paths:
      - 'k8s-manifests/**'

jobs:
  analyze-kubernetes:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install K8s Tools
      run: |
        pip install k8s-analyzer k8s-reporter
    
    - name: Export cluster state
      if: github.event_name == 'schedule'
      env:
        KUBECONFIG: ${{ secrets.KUBECONFIG }}
      run: |
        mkdir -p analysis-results
        kubectl get all --all-namespaces -o yaml > analysis-results/cluster-export.yaml
    
    - name: Analyze Kubernetes manifests
      run: |
        mkdir -p analysis-results
        
        # Analyze local manifests if they exist
        if [ -d "k8s-manifests" ]; then
          k8s-analyzer batch-analyze k8s-manifests \
            --output analysis-results/manifest-analysis.json
          
          k8s-analyzer export-directory-sqlite k8s-manifests \
            analysis-results/manifests.db
        fi
        
        # Analyze cluster export if it exists
        if [ -f "analysis-results/cluster-export.yaml" ]; then
          k8s-analyzer analyze analysis-results/cluster-export.yaml \
            --output analysis-results/cluster-analysis.json
          
          k8s-analyzer export-sqlite analysis-results/cluster-export.yaml \
            analysis-results/cluster.db
          
          k8s-analyzer report analysis-results/cluster-export.yaml \
            --output analysis-results/cluster-report.html
        fi
    
    - name: Generate summary reports
      run: |
        # Generate summaries for each database
        for db in analysis-results/*.db; do
          if [ -f "$db" ]; then
            echo "=== Summary for $(basename $db) ===" >> analysis-results/summary.txt
            k8s-analyzer db-summary "$db" >> analysis-results/summary.txt
            echo "" >> analysis-results/summary.txt
            
            # Check for issues
            k8s-analyzer query-db "$db" --issues >> analysis-results/issues.txt
          fi
        done
    
    - name: Upload analysis results
      uses: actions/upload-artifact@v4
      with:
        name: k8s-analysis-results-${{ github.run_number }}
        path: analysis-results/
        retention-days: 30
    
    - name: Check for critical issues
      run: |
        # Fail the build if critical issues are found
        if [ -f "analysis-results/issues.txt" ] && [ -s "analysis-results/issues.txt" ]; then
          echo "Critical issues found in Kubernetes resources:"
          cat analysis-results/issues.txt
          exit 1
        fi
```

### Jenkins Pipeline

```groovy
// Jenkinsfile for K8s analysis pipeline
pipeline {
    agent any
    
    environment {
        ANALYSIS_DIR = "analysis-${BUILD_NUMBER}"
        DB_FILE = "${ANALYSIS_DIR}/cluster.db"
    }
    
    triggers {
        cron('0 6 * * *')  // Daily at 6 AM
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'mkdir -p ${ANALYSIS_DIR}'
                sh 'pip install k8s-analyzer k8s-reporter'
            }
        }
        
        stage('Export Cluster State') {
            when {
                triggeredBy 'TimerTrigger'
            }
            steps {
                withKubeConfig([credentialsId: 'k8s-config']) {
                    sh '''
                        kubectl get all --all-namespaces -o yaml > ${ANALYSIS_DIR}/cluster-export.yaml
                        kubectl get pv,pvc --all-namespaces -o yaml >> ${ANALYSIS_DIR}/cluster-export.yaml
                    '''
                }
            }
        }
        
        stage('Analyze Resources') {
            parallel {
                stage('Analyze Manifests') {
                    when {
                        changeset 'k8s-manifests/**'
                    }
                    steps {
                        sh '''
                            k8s-analyzer batch-analyze k8s-manifests \
                                --output ${ANALYSIS_DIR}/manifest-analysis.json
                            k8s-analyzer export-directory-sqlite k8s-manifests \
                                ${ANALYSIS_DIR}/manifests.db
                        '''
                    }
                }
                
                stage('Analyze Cluster') {
                    when {
                        fileExists '${ANALYSIS_DIR}/cluster-export.yaml'
                    }
                    steps {
                        sh '''
                            k8s-analyzer analyze ${ANALYSIS_DIR}/cluster-export.yaml \
                                --output ${ANALYSIS_DIR}/cluster-analysis.json
                            k8s-analyzer export-sqlite ${ANALYSIS_DIR}/cluster-export.yaml \
                                ${DB_FILE}
                        '''
                    }
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                sh '''
                    # Generate HTML reports
                    for yaml_file in ${ANALYSIS_DIR}/*.yaml; do
                        if [ -f "$yaml_file" ]; then
                            base_name=$(basename "$yaml_file" .yaml)
                            k8s-analyzer report "$yaml_file" \
                                --output "${ANALYSIS_DIR}/${base_name}-report.html"
                        fi
                    done
                    
                    # Generate database summaries
                    for db_file in ${ANALYSIS_DIR}/*.db; do
                        if [ -f "$db_file" ]; then
                            base_name=$(basename "$db_file" .db)
                            k8s-analyzer db-summary "$db_file" > \
                                "${ANALYSIS_DIR}/${base_name}-summary.txt"
                        fi
                    done
                '''
            }
        }
        
        stage('Quality Gates') {
            steps {
                script {
                    sh '''
                        # Check for resources with issues
                        for db_file in ${ANALYSIS_DIR}/*.db; do
                            if [ -f "$db_file" ]; then
                                issue_count=$(k8s-analyzer query-db "$db_file" --issues | wc -l)
                                echo "Issues found in $(basename $db_file): $issue_count"
                                
                                if [ "$issue_count" -gt 10 ]; then
                                    echo "QUALITY GATE FAILED: Too many issues found"
                                    exit 1
                                fi
                            fi
                        done
                    '''
                }
            }
        }
        
        stage('Deploy Dashboard') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    # Kill any existing dashboard
                    pkill -f k8s-reporter || true
                    
                    # Start new dashboard in background
                    nohup k8s-reporter \
                        --database ${DB_FILE} \
                        --host 0.0.0.0 \
                        --port 8080 \
                        --headless > dashboard.log 2>&1 &
                    
                    echo "Dashboard started at http://localhost:8080"
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '${ANALYSIS_DIR}/**/*', 
                            allowEmptyArchive: true
        }
        failure {
            emailext (
                subject: "K8s Analysis Pipeline Failed - Build ${BUILD_NUMBER}",
                body: """The Kubernetes analysis pipeline has failed.
                         Please check the build logs for details.
                         
                         Build URL: ${BUILD_URL}""",
                to: '${DEFAULT_RECIPIENTS}'
            )
        }
    }
}
```

## Performance Optimization

### Large-Scale Processing

```bash
#!/bin/bash
# Optimized processing for large numbers of files

SOURCE_DIR="$1"
MAX_CONCURRENT="${2:-4}"
BATCH_SIZE="${3:-50}"

if [ -z "$SOURCE_DIR" ]; then
    echo "Usage: $0 <source-directory> [max-concurrent] [batch-size]"
    exit 1
fi

echo "Processing directory: $SOURCE_DIR"
echo "Max concurrent jobs: $MAX_CONCURRENT"
echo "Batch size: $BATCH_SIZE"

# Create output directory
OUTPUT_DIR="./bulk-processing-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Function to process a batch of files
process_batch() {
    local batch_id="$1"
    local batch_files="$2"
    local batch_output="$OUTPUT_DIR/batch-$batch_id"
    
    mkdir -p "$batch_output"
    
    echo "Processing batch $batch_id..."
    
    # Create temporary directory with batch files
    temp_dir="/tmp/k8s-batch-$batch_id"
    mkdir -p "$temp_dir"
    
    # Copy files to temp directory
    echo "$batch_files" | while read -r file; do
        if [ -n "$file" ]; then
            cp "$file" "$temp_dir/"
        fi
    done
    
    # Process the batch
    k8s-analyzer batch-analyze "$temp_dir" \
        --output "$batch_output/analysis.json" \
        --max-files "$BATCH_SIZE"
    
    k8s-analyzer export-directory-sqlite "$temp_dir" \
        "$batch_output/batch.db"
    
    # Cleanup
    rm -rf "$temp_dir"
    
    echo "Batch $batch_id complete"
}

# Find all Kubernetes files
echo "Discovering files..."
k8s-analyzer list-files "$SOURCE_DIR" --recursive > "$OUTPUT_DIR/all-files.txt"

# Split files into batches
total_files=$(wc -l < "$OUTPUT_DIR/all-files.txt")
total_batches=$(( (total_files + BATCH_SIZE - 1) / BATCH_SIZE ))

echo "Found $total_files files, creating $total_batches batches"

# Process batches in parallel
batch_id=0
while IFS= read -r -d '' file; do
    batch_files+=("$file")
    
    if [ ${#batch_files[@]} -eq "$BATCH_SIZE" ] || [ "$batch_id" -eq "$total_batches" ]; then
        # Wait if we've reached max concurrent jobs
        while [ $(jobs -r | wc -l) -ge "$MAX_CONCURRENT" ]; do
            sleep 1
        done
        
        # Process batch in background
        printf '%s\n' "${batch_files[@]}" | process_batch "$batch_id" &
        
        # Reset for next batch
        batch_files=()
        ((batch_id++))
    fi
done < <(find "$SOURCE_DIR" -name "*.yaml" -o -name "*.yml" -o -name "*.json" | head -1000 | tr '\n' '\0')

# Wait for all background jobs to complete
wait

echo "All batches processed. Consolidating results..."

# Consolidate all batch databases
CONSOLIDATED_DB="$OUTPUT_DIR/consolidated.db"
first_db=true

for batch_db in "$OUTPUT_DIR"/batch-*/batch.db; do
    if [ -f "$batch_db" ]; then
        if [ "$first_db" = true ]; then
            cp "$batch_db" "$CONSOLIDATED_DB"
            first_db=false
        else
            # Merge databases (simplified - would need custom script for real merging)
            echo "Would merge $batch_db into consolidated database"
        fi
    fi
done

echo "Bulk processing complete. Results in: $OUTPUT_DIR"
echo "Consolidated database: $CONSOLIDATED_DB"
```

## Best Practices

### Error Handling and Logging

- Always use `--verbose` flag for debugging
- Implement proper error handling in scripts
- Use structured logging with timestamps
- Store logs in centralized locations

### Resource Management

- Use `--max-files` to prevent memory issues
- Implement batch processing for large datasets
- Monitor disk space when generating reports
- Clean up temporary files after processing

### Security Considerations

- Store sensitive kubeconfig files securely
- Use proper file permissions for database files
- Implement access controls for web dashboards
- Audit analysis results for sensitive information

## Related Documentation

- [Basic Usage](basic-usage.md)
- [Multi-cluster Analysis](multi-cluster.md)
- [Custom Dashboards](custom-dashboards.md)
- [CI/CD Integration](../deployment/cicd.md)
