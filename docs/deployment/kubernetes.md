# Kubernetes Deployment [planned/on study]

This guide covers deploying K8s Tools on a Kubernetes cluster, including helm chart setup, configurations, and deployment strategies.

## Overview

Kubernetes deployment provides:

- **Scalability**: Efficient resource utilization
- **High Availability**: Robustness and fault tolerance
- **Integration**: Seamless operation with other Kubernetes workloads

## Prerequisites

- **Kubernetes Cluster**: Version 1.21+
- **Helm**: Version 3+
- **kubectl**: Configured to access the target cluster

## Helm Chart Deployment

### Adding Helm Repository

Add the K8s Tools Helm repository:

```bash
helm repo add k8s-tools https://k8s-tools.github.io/helm-charts
helm repo update
```

### Installing the Chart

Install the K8s Tools chart with default values:

```bash
helm install k8s-tools k8s-tools/k8s-tools --namespace tools
```

### Customizing Values

Customize the deployment using a `values.yaml` file:

```yaml
replicaCount: 1
resourceLimits:
  cpu: "1000m"
  memory: "512Mi"

service:
  type: NodePort
  port: 8080
  nodePort: 31000

config:
  kubeConfig: "/config/kubeconfig"

featureFlags:
  enableBatchProcessing: true
```

Apply the custom values:

```bash
helm upgrade k8s-tools k8s-tools/k8s-tools --namespace tools -f values.yaml
```

## Deploying with Manifests

### Basic Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k8s-tools
  namespace: tools
spec:
  replicas: 2
  selector:
    matchLabels:
      app: k8s-tools
  template:
    metadata:
      labels:
        app: k8s-tools
    spec:
      containers:
      - name: k8s-tools
        image: k8stools/k8s-tools:latest
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "500m"
            memory: "256Mi"
        volumeMounts:
        - name: kubeconfig
          mountPath: /config
      volumes:
      - name: kubeconfig
        configMap:
          name: kube-config
```

### Service Manifest

Expose the application using a LoadBalancer or NodePort:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: k8s-tools
  namespace: tools
spec:
  type: LoadBalancer
  ports:
  - port: 8080
    targetPort: 8080
  selector:
    app: k8s-tools
```

### Creating ConfigMap

Create a ConfigMap for configuration files:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-config
  namespace: tools
data:
  kubeconfig: |
    apiVersion: v1
    kind: Config
    clusters:
    - cluster:
        server: https://k8s.example.com:6443
        certificate-authority-data: ...
      name: example-cluster
    contexts:
    - context:
        cluster: example-cluster
        user: admin
      name: example-context
    current-context: example-context
    users:
    - name: admin
      user:
        client-certificate-data: ...
        client-key-data: ...
```

Deploy the resources:

```bash
kubectl apply -f k8s-tools-deployment.yaml
kubectl apply -f k8s-tools-service.yaml
kubectl apply -f k8s-tools-configmap.yaml
```

## Managing Deployments

### Scaling

Scale the deployment using kubectl:

```bash
kubectl scale deployment/k8s-tools --replicas=5 -n tools
```

### Rolling Updates

Update the deployment incrementally:

```bash
kubectl rollout status deployment/k8s-tools -n tools
kubectl set image deployment/k8s-tools k8s-tools=k8stools/k8s-tools:latest -n tools
```

### Monitoring

Monitor the deployment status and health:

```bash
kubectl get pods -n tools
kubectl describe deployment/k8s-tools -n tools
kubectl logs -l app=k8s-tools -n tools
```

## Security Considerations

### RBAC

Ensure that the deployment has appropriate Role-Based Access Control (RBAC) settings:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: tools-role
  namespace: tools
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: tools-rolebinding
  namespace: tools
subjects:
- kind: ServiceAccount
  name: default
  namespace: tools
roleRef:
  kind: Role
  name: tools-role
  apiGroup: rbac.authorization.k8s.io
```

### Network Policies

Define network policies to restrict access:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web
  namespace: tools
spec:
  podSelector:
    matchLabels:
      app: k8s-tools
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/24
```

## Troubleshooting

### Common Issues

#### Pod Failures

```bash
kubectl describe pod POD_NAME -n tools

# Check events and logs
kubectl get events -n tools
kubectl logs POD_NAME -n tools
```

#### Service Access

```bash
# Check service configuration
kubectl get service k8s-tools -n tools

# Describe the service
kubectl describe service k8s-tools -n tools
```

## Best Practices

### Configuration Management

1. **Use Helm**: For advanced templating and configuration
2. **Version Control**: Keep Kubernetes manifests and Helm charts in version control
3. **Environment Separation**: Use different namespaces for test and production

### Monitoring and Logging

1. **Integrate with Prometheus/Grafana**: For metrics collection and visualization
2. **Use ELK Stack**: For centralized logging
3. **Set Alerts**: Use alerts for critical metrics

## Related Documentation

- [Docker Deployment](docker.md)
- [CI/CD Integration](cicd.md)
