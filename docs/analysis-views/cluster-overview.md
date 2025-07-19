# Cluster Overview

The Cluster Overview provides a comprehensive high-level view of your Kubernetes cluster's health, resource utilization, and key metrics.

## Overview

This analysis view presents:

- **Cluster Summary**: Basic information about nodes, namespaces, and workloads
- **Resource Utilization**: CPU, memory, and storage usage across the cluster
- **Node Status**: Health and capacity of cluster nodes
- **Workload Distribution**: How applications are distributed across nodes
- **Recent Events**: Important cluster events and alerts

## Key Metrics

### Node Information
- Total nodes and their status (Ready, NotReady, Unknown)
- Node capacity and allocatable resources
- Node labels and taints

### Resource Usage
- CPU and memory utilization percentages
- Storage consumption and available capacity
- Network traffic and pod-to-pod communication

### Workload Summary
- Total pods, deployments, services, and other resources
- Pod distribution across namespaces
- Resource requests vs. limits

## Using the Cluster Overview

```bash
k8s-analyzer analyze --view cluster-overview
```

## Interpreting Results

The cluster overview helps you quickly identify:

- Resource bottlenecks
- Unhealthy nodes
- Overcommitted resources
- Uneven workload distribution

## Related Views

- [Resource Efficiency](resource-efficiency.md)
- [Health Dashboard](health-dashboard.md)
- [Namespace Analysis](namespace-analysis.md)
