# 🚀 k8s-analyzer Examples

This document provides comprehensive examples and use cases for k8s-analyzer, demonstrating real-world scenarios and common workflows.

## Quick Start Examples

### Basic Analysis

```bash
# Analyze current cluster
k8s-analyzer analyze

# Parse local YAML files and analyze
k8s-analyzer parse ./manifests/ --output cluster-state.json
k8s-analyzer analyze cluster-state.json --output analysis.json

# Generate a comprehensive report
k8s-analyzer report analysis.json --format html --output cluster-report.html
```

### Single Command Workflow

```bash
# Complete analysis from YAML files to HTML report
k8s-analyzer parse ./k8s-manifests/ | \
k8s-analyzer analyze --stdin | \
k8s-analyzer report --stdin --format html --output production-cluster-analysis.html
```

## Real-World Scenarios

### 1. Production Cluster Health Check

**Scenario**: Daily health assessment of a production Kubernetes cluster.

```bash
#!/bin/bash
# production-health-check.sh

DATE=$(date +%Y-%m-%d)
REPORT_DIR="./reports/$DATE"
mkdir -p "$REPORT_DIR"

echo "🔍 Starting production cluster health check for $DATE"

# 1. Analyze current cluster state
k8s-analyzer analyze \
    --output "$REPORT_DIR/cluster-analysis.json" \
    --verbose

# 2. Generate HTML dashboard
k8s-analyzer report "$REPORT_DIR/cluster-analysis.json" \
    --format html \
    --output "$REPORT_DIR/health-dashboard.html" \
    --include-graphs

# 3. Export to SQLite for historical tracking
k8s-analyzer sqlite "$REPORT_DIR/cluster-analysis.json" \
    --database "./historical/cluster-health.db" \
    --table-prefix "prod_$DATE"

# 4. Generate CSV for spreadsheet analysis
k8s-analyzer csv "$REPORT_DIR/cluster-analysis.json" \
    --output "$REPORT_DIR/resources.csv" \
    --include-relationships

# 5. Check for critical issues
CRITICAL_ISSUES=$(jq '.resources[] | select(.health_status == "error") | length' "$REPORT_DIR/cluster-analysis.json")

if [ "$CRITICAL_ISSUES" -gt 0 ]; then
    echo "⚠️  Found $CRITICAL_ISSUES critical issues!"
    
    # Generate focused report on critical issues
    k8s-analyzer report "$REPORT_DIR/cluster-analysis.json" \
        --format json \
        --filter "health_status=error" \
        --output "$REPORT_DIR/critical-issues.json"
    
    # Send alert (integrate with your alerting system)
    curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
        -H 'Content-type: application/json' \
        --data "{\"text\":\"🚨 Production cluster has $CRITICAL_ISSUES critical issues. Check: $REPORT_DIR/health-dashboard.html\"}"
fi

echo "✅ Health check complete. Dashboard: $REPORT_DIR/health-dashboard.html"
```

### 2. Multi-Environment Comparison

**Scenario**: Compare configurations across development, staging, and production environments.

```bash
#!/bin/bash
# multi-env-analysis.sh

ENVIRONMENTS=("dev" "staging" "prod")
BASE_DIR="./environment-analysis"
mkdir -p "$BASE_DIR"

for ENV in "${ENVIRONMENTS[@]}"; do
    echo "🔍 Analyzing $ENV environment"
    
    # Switch kubectl context
    kubectl config use-context "$ENV-cluster"
    
    # Analyze environment
    k8s-analyzer analyze \
        --namespace-filter "app-*" \
        --output "$BASE_DIR/$ENV-analysis.json"
    
    # Generate environment-specific report
    k8s-analyzer report "$BASE_DIR/$ENV-analysis.json" \
        --format html \
        --output "$BASE_DIR/$ENV-report.html" \
        --title "$ENV Environment Analysis"
done

# Generate comparison report
echo "📊 Generating comparison report"
python3 << EOF
import json
import pandas as pd

environments = ['dev', 'staging', 'prod']
comparison_data = []

for env in environments:
    with open(f'$BASE_DIR/{env}-analysis.json', 'r') as f:
        data = json.load(f)
    
    summary = data.get('summary', {})
    comparison_data.append({
        'Environment': env,
        'Total Resources': summary.get('total_resources', 0),
        'Healthy': summary.get('health_distribution', {}).get('healthy', 0),
        'Warning': summary.get('health_distribution', {}).get('warning', 0),
        'Error': summary.get('health_distribution', {}).get('error', 0),
        'Namespaces': len(summary.get('namespaces', [])),
        'Resource Types': len(summary.get('resource_type_distribution', {}))
    })

df = pd.DataFrame(comparison_data)
df.to_csv('$BASE_DIR/environment-comparison.csv', index=False)
print("Comparison saved to environment-comparison.csv")
EOF
```

### 3. Application Dependency Mapping

**Scenario**: Map dependencies for a specific application across namespaces.

```bash
#!/bin/bash
# app-dependency-analysis.sh

APP_NAME="ecommerce-app"
OUTPUT_DIR="./dependency-analysis/$APP_NAME"
mkdir -p "$OUTPUT_DIR"

echo "🔗 Analyzing dependencies for $APP_NAME"

# 1. Parse all manifests related to the app
find ./manifests/ -name "*$APP_NAME*" -type f \( -name "*.yaml" -o -name "*.yml" \) | \
k8s-analyzer parse --from-stdin --output "$OUTPUT_DIR/app-resources.json"

# 2. Analyze the parsed resources
k8s-analyzer analyze "$OUTPUT_DIR/app-resources.json" \
    --output "$OUTPUT_DIR/app-analysis.json" \
    --focus-on-relationships

# 3. Generate dependency graph
k8s-analyzer graph "$OUTPUT_DIR/app-analysis.json" \
    --output "$OUTPUT_DIR/dependency-graph.dot" \
    --format dot \
    --include-external-dependencies

# Convert DOT to SVG for viewing
if command -v dot &> /dev/null; then
    dot -Tsvg "$OUTPUT_DIR/dependency-graph.dot" -o "$OUTPUT_DIR/dependency-graph.svg"
    echo "📊 Dependency graph: $OUTPUT_DIR/dependency-graph.svg"
fi

# 4. Generate focused report
k8s-analyzer report "$OUTPUT_DIR/app-analysis.json" \
    --format html \
    --output "$OUTPUT_DIR/dependency-report.html" \
    --title "$APP_NAME Dependency Analysis" \
    --include-relationships \
    --include-graphs

# 5. Export relationship data for further analysis
jq '.relationships[] | select(.metadata.app_name == "'$APP_NAME'")' \
    "$OUTPUT_DIR/app-analysis.json" > "$OUTPUT_DIR/app-relationships.json"

echo "✅ Dependency analysis complete for $APP_NAME"
echo "📋 Report: $OUTPUT_DIR/dependency-report.html"
echo "🔗 Relationships: $OUTPUT_DIR/app-relationships.json"
```

### 4. Security Compliance Scan

**Scenario**: Scan cluster for security best practices and compliance issues.

```bash
#!/bin/bash
# security-compliance-scan.sh

SCAN_DATE=$(date +%Y-%m-%d_%H-%M-%S)
SECURITY_DIR="./security-scans/$SCAN_DATE"
mkdir -p "$SECURITY_DIR"

echo "🔒 Starting security compliance scan"

# 1. Analyze cluster with security focus
k8s-analyzer analyze \
    --output "$SECURITY_DIR/cluster-analysis.json" \
    --include-security-checks \
    --verbose

# 2. Extract security-related issues
jq '.resources[] | select(.issues | length > 0) | {
    name: .metadata.name,
    namespace: .metadata.namespace,
    kind: .kind,
    issues: .issues,
    security_score: .security_score // "unknown"
}' "$SECURITY_DIR/cluster-analysis.json" > "$SECURITY_DIR/security-issues.json"

# 3. Check for common security misconfigurations
python3 << 'EOF'
import json
import sys

with open(f"$SECURITY_DIR/cluster-analysis.json") as f:
    data = json.load(f)

security_findings = {
    "privileged_containers": [],
    "no_resource_limits": [],
    "default_service_accounts": [],
    "hostnetwork_pods": [],
    "root_users": [],
    "no_security_context": []
}

for resource in data.get('resources', []):
    if resource['kind'] == 'Pod':
        spec = resource.get('spec', {})
        containers = spec.get('containers', [])
        
        # Check for privileged containers
        for container in containers:
            security_context = container.get('securityContext', {})
            if security_context.get('privileged', False):
                security_findings['privileged_containers'].append({
                    'name': resource['metadata']['name'],
                    'namespace': resource['metadata']['namespace'],
                    'container': container['name']
                })
            
            # Check for missing resource limits
            if 'resources' not in container or 'limits' not in container.get('resources', {}):
                security_findings['no_resource_limits'].append({
                    'name': resource['metadata']['name'],
                    'namespace': resource['metadata']['namespace'],
                    'container': container['name']
                })
        
        # Check for hostNetwork
        if spec.get('hostNetwork', False):
            security_findings['hostnetwork_pods'].append({
                'name': resource['metadata']['name'],
                'namespace': resource['metadata']['namespace']
            })
        
        # Check for default service account usage
        service_account = spec.get('serviceAccountName', 'default')
        if service_account == 'default':
            security_findings['default_service_accounts'].append({
                'name': resource['metadata']['name'],
                'namespace': resource['metadata']['namespace']
            })

with open(f"$SECURITY_DIR/security-findings.json", 'w') as f:
    json.dump(security_findings, f, indent=2)

# Generate summary
total_issues = sum(len(v) for v in security_findings.values())
print(f"🔍 Security scan complete. Found {total_issues} potential issues.")

for category, findings in security_findings.items():
    if findings:
        print(f"  - {category.replace('_', ' ').title()}: {len(findings)} issues")
EOF

# 4. Generate security report
k8s-analyzer report "$SECURITY_DIR/cluster-analysis.json" \
    --format html \
    --output "$SECURITY_DIR/security-report.html" \
    --title "Security Compliance Scan - $SCAN_DATE" \
    --filter "health_status=warning,error" \
    --include-security-recommendations

echo "✅ Security scan complete"
echo "📋 Report: $SECURITY_DIR/security-report.html"
echo "🔍 Findings: $SECURITY_DIR/security-findings.json"
```

### 5. Migration Planning

**Scenario**: Analyze resources before a major cluster migration or upgrade.

```bash
#!/bin/bash
# migration-planning.sh

MIGRATION_ID="v1.28-upgrade-$(date +%Y%m%d)"
MIGRATION_DIR="./migrations/$MIGRATION_ID"
mkdir -p "$MIGRATION_DIR"

echo "📋 Planning migration: $MIGRATION_ID"

# 1. Full cluster analysis
k8s-analyzer analyze \
    --output "$MIGRATION_DIR/pre-migration-state.json" \
    --include-deprecated-apis \
    --include-version-compatibility

# 2. Identify deprecated APIs
jq '.resources[] | select(.api_version | test("v1beta1|extensions/v1beta1")) | {
    name: .metadata.name,
    namespace: .metadata.namespace,
    kind: .kind,
    api_version: .api_version,
    replacement_api: .migration_info.replacement_api // "manual_check_required"
}' "$MIGRATION_DIR/pre-migration-state.json" > "$MIGRATION_DIR/deprecated-apis.json"

# 3. Check for version compatibility issues
python3 << 'EOF'
import json

with open(f"$MIGRATION_DIR/pre-migration-state.json") as f:
    data = json.load(f)

compatibility_issues = []
target_version = "1.28"

for resource in data.get('resources', []):
    api_version = resource.get('api_version', '')
    kind = resource.get('kind', '')
    
    # Check for known compatibility issues
    issues = []
    
    if api_version == "extensions/v1beta1" and kind == "Ingress":
        issues.append("Ingress extensions/v1beta1 removed in v1.22, use networking.k8s.io/v1")
    
    if api_version == "v1beta1" and kind in ["CronJob"]:
        issues.append(f"{kind} v1beta1 deprecated, use batch/v1")
    
    if resource.get('spec', {}).get('containers'):
        for container in resource['spec']['containers']:
            image = container.get('image', '')
            if ':latest' in image:
                issues.append(f"Container {container['name']} uses ':latest' tag, pin to specific version")
    
    if issues:
        compatibility_issues.append({
            'resource': f"{resource['metadata']['namespace']}/{resource['metadata']['name']}",
            'kind': kind,
            'api_version': api_version,
            'issues': issues
        })

with open(f"$MIGRATION_DIR/compatibility-issues.json", 'w') as f:
    json.dump(compatibility_issues, f, indent=2)

print(f"Found {len(compatibility_issues)} compatibility issues")
EOF

# 4. Generate migration checklist
cat > "$MIGRATION_DIR/migration-checklist.md" << 'EOF'
# Migration Checklist for $MIGRATION_ID

## Pre-Migration Steps
- [ ] Backup current cluster state
- [ ] Review deprecated APIs (see deprecated-apis.json)
- [ ] Update manifests with compatibility issues
- [ ] Test applications in staging environment
- [ ] Prepare rollback plan

## API Version Updates Required
EOF

jq -r '.[] | "- [ ] Update \(.kind) \(.resource) from \(.api_version)"' \
    "$MIGRATION_DIR/deprecated-apis.json" >> "$MIGRATION_DIR/migration-checklist.md"

cat >> "$MIGRATION_DIR/migration-checklist.md" << 'EOF'

## Post-Migration Verification
- [ ] Verify all pods are running
- [ ] Check service connectivity
- [ ] Validate persistent volume claims
- [ ] Run application health checks
- [ ] Monitor cluster metrics

## Resources
- Pre-migration state: pre-migration-state.json
- Compatibility issues: compatibility-issues.json
- Deprecated APIs: deprecated-apis.json
EOF

# 5. Generate pre-migration report
k8s-analyzer report "$MIGRATION_DIR/pre-migration-state.json" \
    --format html \
    --output "$MIGRATION_DIR/pre-migration-report.html" \
    --title "Pre-Migration Analysis - $MIGRATION_ID" \
    --include-migration-recommendations

echo "✅ Migration planning complete"
echo "📋 Checklist: $MIGRATION_DIR/migration-checklist.md"
echo "📊 Report: $MIGRATION_DIR/pre-migration-report.html"
```

## CI/CD Integration Examples

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/k8s-analysis.yml
name: Kubernetes Analysis

on:
  pull_request:
    paths:
      - 'k8s/**'
      - 'manifests/**'
  push:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup k8s-analyzer
        run: |
          curl -LO https://github.com/your-org/k8s-analyzer/releases/latest/download/k8s-analyzer-linux
          chmod +x k8s-analyzer-linux
          sudo mv k8s-analyzer-linux /usr/local/bin/k8s-analyzer
      
      - name: Analyze Kubernetes manifests
        run: |
          k8s-analyzer parse ./k8s/ --output cluster-state.json
          k8s-analyzer analyze cluster-state.json --output analysis.json
          k8s-analyzer validate analysis.json --strict
      
      - name: Generate report
        run: |
          k8s-analyzer report analysis.json --format html --output k8s-analysis-report.html
          k8s-analyzer csv analysis.json --output resources.csv
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: k8s-analysis-results
          path: |
            k8s-analysis-report.html
            resources.csv
            analysis.json
      
      - name: Comment PR with summary
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const analysis = JSON.parse(fs.readFileSync('analysis.json'));
            const summary = analysis.summary;
            
            const comment = `## 🔍 Kubernetes Analysis Results
            
            **Resources Analyzed:** ${summary.total_resources}
            **Health Status:**
            - ✅ Healthy: ${summary.health_distribution.healthy || 0}
            - ⚠️ Warning: ${summary.health_distribution.warning || 0}
            - ❌ Error: ${summary.health_distribution.error || 0}
            
            **Resource Types:** ${Object.keys(summary.resource_type_distribution).join(', ')}
            
            [📊 View Full Report](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 2. GitLab CI/CD Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - report
  - deploy

variables:
  K8S_ANALYZER_VERSION: "latest"

k8s-analysis:
  stage: analyze
  image: alpine:latest
  before_script:
    - apk add --no-cache curl jq
    - curl -LO https://github.com/your-org/k8s-analyzer/releases/latest/download/k8s-analyzer-linux
    - chmod +x k8s-analyzer-linux
    - mv k8s-analyzer-linux /usr/local/bin/k8s-analyzer
  script:
    - k8s-analyzer parse ./manifests/ --output cluster-state.json
    - k8s-analyzer analyze cluster-state.json --output analysis.json
    - k8s-analyzer validate analysis.json
    - k8s-analyzer report analysis.json --format html --output k8s-report.html
    - |
      CRITICAL_ISSUES=$(jq '.resources[] | select(.health_status == "error") | length' analysis.json)
      if [ "$CRITICAL_ISSUES" -gt 0 ]; then
        echo "❌ Found $CRITICAL_ISSUES critical issues!"
        exit 1
      fi
  artifacts:
    reports:
      junit: analysis.json
    paths:
      - k8s-report.html
      - analysis.json
    expire_in: 1 week
  only:
    changes:
      - manifests/**/*
      - k8s/**/*
```

## Advanced Use Cases

### 1. Automated Resource Optimization

```bash
#!/bin/bash
# resource-optimization.sh

echo "🔧 Starting resource optimization analysis"

# Analyze current resource usage
k8s-analyzer analyze --include-resource-usage --output current-state.json

# Generate optimization recommendations
python3 << 'EOF'
import json

with open('current-state.json') as f:
    data = json.load(f)

recommendations = []

for resource in data.get('resources', []):
    if resource['kind'] == 'Pod':
        containers = resource.get('spec', {}).get('containers', [])
        
        for container in containers:
            requests = container.get('resources', {}).get('requests', {})
            limits = container.get('resources', {}).get('limits', {})
            
            # Check for over-provisioning
            if 'memory' in requests and 'memory' in limits:
                memory_ratio = int(limits['memory'].rstrip('Mi')) / int(requests['memory'].rstrip('Mi'))
                if memory_ratio > 4:
                    recommendations.append({
                        'type': 'memory_optimization',
                        'resource': f"{resource['metadata']['namespace']}/{resource['metadata']['name']}",
                        'container': container['name'],
                        'current_ratio': memory_ratio,
                        'recommendation': 'Consider reducing memory limits or increasing requests'
                    })
            
            # Check for missing resource specifications
            if not requests:
                recommendations.append({
                    'type': 'missing_requests',
                    'resource': f"{resource['metadata']['namespace']}/{resource['metadata']['name']}",
                    'container': container['name'],
                    'recommendation': 'Add resource requests for better scheduling'
                })

with open('optimization-recommendations.json', 'w') as f:
    json.dump(recommendations, f, indent=2)

print(f"Generated {len(recommendations)} optimization recommendations")
EOF

k8s-analyzer report current-state.json \
    --format html \
    --output optimization-report.html \
    --title "Resource Optimization Analysis" \
    --include-recommendations
```

### 2. Compliance Monitoring

```bash
#!/bin/bash
# compliance-monitoring.sh

COMPLIANCE_STANDARDS=("pci-dss" "sox" "hipaa")
DATE=$(date +%Y-%m-%d)

for STANDARD in "${COMPLIANCE_STANDARDS[@]}"; do
    echo "📋 Checking $STANDARD compliance"
    
    k8s-analyzer analyze \
        --compliance-standard "$STANDARD" \
        --output "compliance-$STANDARD-$DATE.json"
    
    # Generate compliance report
    k8s-analyzer report "compliance-$STANDARD-$DATE.json" \
        --format html \
        --output "compliance-$STANDARD-report-$DATE.html" \
        --title "$STANDARD Compliance Report" \
        --include-compliance-details
    
    # Export violations for tracking
    jq '.compliance_violations // []' "compliance-$STANDARD-$DATE.json" \
        > "violations-$STANDARD-$DATE.json"
done

# Generate combined compliance dashboard
k8s-analyzer report compliance-*-$DATE.json \
    --format html \
    --output "combined-compliance-dashboard-$DATE.html" \
    --title "Multi-Standard Compliance Dashboard"
```

### 3. Disaster Recovery Planning

```bash
#!/bin/bash
# disaster-recovery-analysis.sh

echo "🔄 Analyzing cluster for disaster recovery planning"

# Full cluster state capture
k8s-analyzer analyze \
    --include-persistent-volumes \
    --include-secrets \
    --include-configmaps \
    --output dr-baseline.json

# Identify critical resources
jq '.resources[] | select(
    (.metadata.labels.critical == "true") or 
    (.metadata.annotations."backup.priority" == "high") or
    (.kind == "PersistentVolumeClaim")
) | {
    name: .metadata.name,
    namespace: .metadata.namespace,
    kind: .kind,
    priority: (.metadata.annotations."backup.priority" // "medium"),
    dependencies: [.relationships[].target.name]
}' dr-baseline.json > critical-resources.json

# Generate backup strategy
python3 << 'EOF'
import json

with open('dr-baseline.json') as f:
    data = json.load(f)

backup_plan = {
    "immediate_backup": [],
    "daily_backup": [],
    "weekly_backup": []
}

for resource in data.get('resources', []):
    priority = resource.get('metadata', {}).get('annotations', {}).get('backup.priority', 'low')
    
    backup_item = {
        'name': resource['metadata']['name'],
        'namespace': resource['metadata']['namespace'],
        'kind': resource['kind'],
        'dependencies': [rel['target']['name'] for rel in resource.get('relationships', [])]
    }
    
    if priority == 'critical':
        backup_plan['immediate_backup'].append(backup_item)
    elif priority == 'high':
        backup_plan['daily_backup'].append(backup_item)
    else:
        backup_plan['weekly_backup'].append(backup_item)

with open('backup-plan.json', 'w') as f:
    json.dump(backup_plan, f, indent=2)
EOF

# Generate DR report
k8s-analyzer report dr-baseline.json \
    --format html \
    --output dr-analysis-report.html \
    --title "Disaster Recovery Analysis" \
    --include-backup-recommendations

echo "✅ DR analysis complete"
echo "📋 Critical resources: critical-resources.json"
echo "🔄 Backup plan: backup-plan.json"
echo "📊 DR Report: dr-analysis-report.html"
```

## Custom Scripts and Integrations

### 1. Slack Integration

```bash
#!/bin/bash
# slack-integration.sh

SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

# Analyze cluster
k8s-analyzer analyze --output daily-analysis.json

# Extract summary
TOTAL_RESOURCES=$(jq '.summary.total_resources' daily-analysis.json)
ERROR_COUNT=$(jq '.summary.health_distribution.error // 0' daily-analysis.json)
WARNING_COUNT=$(jq '.summary.health_distribution.warning // 0' daily-analysis.json)

# Prepare Slack message
if [ "$ERROR_COUNT" -gt 0 ]; then
    STATUS="🚨 CRITICAL"
    COLOR="danger"
elif [ "$WARNING_COUNT" -gt 0 ]; then
    STATUS="⚠️ WARNING"
    COLOR="warning"
else
    STATUS="✅ HEALTHY"
    COLOR="good"
fi

curl -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-type: application/json' \
    --data "{
        \"attachments\": [{
            \"color\": \"$COLOR\",
            \"title\": \"Daily Cluster Health Report\",
            \"fields\": [
                {\"title\": \"Status\", \"value\": \"$STATUS\", \"short\": true},
                {\"title\": \"Total Resources\", \"value\": \"$TOTAL_RESOURCES\", \"short\": true},
                {\"title\": \"Errors\", \"value\": \"$ERROR_COUNT\", \"short\": true},
                {\"title\": \"Warnings\", \"value\": \"$WARNING_COUNT\", \"short\": true}
            ],
            \"footer\": \"k8s-analyzer\",
            \"ts\": $(date +%s)
        }]
    }"
```

### 2. Prometheus Metrics Export

```bash
#!/bin/bash
# prometheus-metrics.sh

# Analyze cluster and extract metrics
k8s-analyzer analyze --output metrics-analysis.json

# Convert to Prometheus format
python3 << 'EOF'
import json
from datetime import datetime

with open('metrics-analysis.json') as f:
    data = json.load(f)

timestamp = int(datetime.now().timestamp() * 1000)
summary = data.get('summary', {})

metrics = [
    f"k8s_analyzer_total_resources {summary.get('total_resources', 0)} {timestamp}",
    f"k8s_analyzer_healthy_resources {summary.get('health_distribution', {}).get('healthy', 0)} {timestamp}",
    f"k8s_analyzer_warning_resources {summary.get('health_distribution', {}).get('warning', 0)} {timestamp}",
    f"k8s_analyzer_error_resources {summary.get('health_distribution', {}).get('error', 0)} {timestamp}",
    f"k8s_analyzer_total_namespaces {len(summary.get('namespaces', []))} {timestamp}"
]

# Add per-namespace metrics
for ns, count in summary.get('namespace_distribution', {}).items():
    safe_ns = ns.replace('-', '_').replace('.', '_')
    metrics.append(f"k8s_analyzer_namespace_resources{{namespace=\"{ns}\"}} {count} {timestamp}")

with open('k8s_analyzer_metrics.prom', 'w') as f:
    f.write('\n'.join(metrics))

print("Metrics exported to k8s_analyzer_metrics.prom")
EOF

# Push to Prometheus Pushgateway (if available)
if command -v curl &> /dev/null && [ -n "$PUSHGATEWAY_URL" ]; then
    curl -X POST "$PUSHGATEWAY_URL/metrics/job/k8s_analyzer" \
        --data-binary @k8s_analyzer_metrics.prom
fi
```

This comprehensive examples document demonstrates various real-world scenarios and use cases for k8s-analyzer, from basic analysis to complex CI/CD integrations and custom monitoring solutions.
