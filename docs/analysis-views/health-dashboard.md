# Health Dashboard

The Health Dashboard provides an at-a-glance view of the overall health of your Kubernetes cluster, with indicators for node health, workload status, and other key metrics.

## Overview

The Health Dashboard includes:

- **Node Health**: Status of nodes in the cluster
- **Workload Health**: Deployment and service health checks
- **Resource Availability**: Current utilization of CPU, memory, and storage
- **Alerting Dashboard**: Active alerts and notifications

## Key Health Metrics

### Node Health Indicators
- **Node Status**: Ready, NotReady, Unknown
- **Capacity and Allocatable Resources**: CPU and memory
- **Node Conditions**: MemoryPressure, DiskPressure, etc.

### Workload Health Indicators
- **Deployment Status**: Pod status and availability
- **Failed Pods**: Recent failures and restarts
- **Service Reachability**: Network and service checks

### Alerting and Notifications
- **Current Alerts**: Active cluster-wide alerts
- **History of Alerts**: Past alerts and resolutions
- **Critical Notifications**: Node and workload alerts

## Usage

To view the health dashboard, use:

```bash
k8s-analyzer dashboard --view health
```

## Integration

### Monitoring Tools
- Prometheus for gathering health metrics
- Grafana for visual representation
- Alertmanager for alerting

## Maintenance Recommendations

1. **Regular Monitoring**: Always keep an eye on the dashboard for real-time indicators.
2. **Alert Response**: Address alerts promptly to mitigate issues.
3. **Capacity Planning**: Use health metrics for long-term planning.

## Related Views

- [Resource Efficiency](resource-efficiency.md)
- [Security Analysis](security-analysis.md)
- [Cluster Overview](cluster-overview.md)
