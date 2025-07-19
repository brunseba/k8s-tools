# Docker Deployment

This guide covers running K8s Tools using Docker containers, including building custom images and deployment strategies.

## Overview

Docker deployment provides:

- **Isolated Environment**: Clean runtime environment
- **Consistent Execution**: Same behavior across platforms
- **Easy Distribution**: Simple image sharing and deployment
- **CI/CD Integration**: Seamless pipeline integration

## Quick Start

### Using Pre-built Images

Pull and run the official K8s Tools Docker image:

```bash
# Pull the latest image
docker pull k8stools/k8s-tools:latest

# Run cluster analysis
docker run --rm \
  -v ~/.kube:/root/.kube:ro \
  -v $(pwd)/reports:/app/reports \
  k8stools/k8s-tools:latest analyze --view cluster-overview
```

### Available Tags

- `latest`: Latest stable release
- `v1.0.0`: Specific version tags
- `dev`: Development builds (bleeding edge)

## Building Custom Images

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY README.md ./

# Install dependencies and application
RUN uv sync --no-dev
RUN uv pip install -e .

# Create non-root user
RUN useradd -m -u 1000 k8stools
USER k8stools

# Set entry point
ENTRYPOINT ["k8s-analyzer"]
CMD ["--help"]
```

### Multi-stage Build

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
COPY src/ src/
RUN uv sync --no-dev

# Runtime stage
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 k8stools

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

USER k8stools
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["k8s-analyzer"]
```

### Building the Image

```bash
# Build with default tag
docker build -t k8s-tools .

# Build with specific tag
docker build -t k8s-tools:v1.0.0 .

# Build with build arguments
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t k8s-tools:python3.11 .
```

## Running Containers

### Basic Usage

```bash
# Simple cluster analysis
docker run --rm \
  -v ~/.kube:/root/.kube:ro \
  k8s-tools analyze

# With custom configuration
docker run --rm \
  -v ~/.kube:/root/.kube:ro \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  k8s-tools analyze --config /app/config.yaml
```

### Volume Mounts

#### Kubeconfig Mount

```bash
# Read-only kubeconfig mount
-v ~/.kube:/root/.kube:ro

# Custom kubeconfig location
-v /path/to/kubeconfig:/app/kubeconfig:ro
```

#### Output Directory

```bash
# Mount output directory
-v $(pwd)/reports:/app/reports

# With specific permissions
-v $(pwd)/reports:/app/reports:Z  # SELinux
```

#### Configuration Files

```bash
# Configuration file
-v $(pwd)/config.yaml:/app/config.yaml:ro

# Configuration directory
-v $(pwd)/configs:/app/configs:ro
```

### Environment Variables

```bash
# Set log level
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -v ~/.kube:/root/.kube:ro \
  k8s-tools analyze

# Override kubeconfig path
docker run --rm \
  -e KUBECONFIG=/app/kubeconfig \
  -v ~/.kube/config:/app/kubeconfig:ro \
  k8s-tools analyze
```

## Docker Compose

### Basic Compose File

```yaml
# docker-compose.yml
version: '3.8'

services:
  k8s-analyzer:
    image: k8stools/k8s-tools:latest
    volumes:
      - ~/.kube:/root/.kube:ro
      - ./reports:/app/reports
      - ./config.yaml:/app/config.yaml:ro
    environment:
      - LOG_LEVEL=INFO
    command: ["analyze", "--config", "/app/config.yaml"]

  k8s-reporter:
    image: k8stools/k8s-tools:latest
    volumes:
      - ./reports:/app/reports:ro
      - ./output:/app/output
    command: ["report", "--input", "/app/reports", "--output", "/app/output"]
    depends_on:
      - k8s-analyzer
```

### Running with Compose

```bash
# Run analysis
docker-compose up k8s-analyzer

# Run full pipeline
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f k8s-analyzer
```

## Advanced Configurations

### Multi-cluster Analysis

```yaml
# docker-compose.multi-cluster.yml
version: '3.8'

services:
  analyze-prod:
    image: k8stools/k8s-tools:latest
    volumes:
      - ./kubeconfigs/prod-config:/root/.kube/config:ro
      - ./reports/prod:/app/reports
    command: ["analyze", "--cluster", "production"]

  analyze-staging:
    image: k8stools/k8s-tools:latest
    volumes:
      - ./kubeconfigs/staging-config:/root/.kube/config:ro
      - ./reports/staging:/app/reports
    command: ["analyze", "--cluster", "staging"]

  consolidate-reports:
    image: k8stools/k8s-tools:latest
    volumes:
      - ./reports:/app/reports:ro
      - ./output:/app/output
    command: ["report", "--multi-cluster", "/app/reports", "--output", "/app/output"]
    depends_on:
      - analyze-prod
      - analyze-staging
```

### Scheduled Analysis

```yaml
# docker-compose.scheduled.yml
version: '3.8'

services:
  scheduler:
    image: k8stools/k8s-tools:latest
    volumes:
      - ~/.kube:/root/.kube:ro
      - ./reports:/app/reports
      - ./scripts:/app/scripts
    environment:
      - SCHEDULE="0 */4 * * *"  # Every 4 hours
    command: ["/app/scripts/scheduled-analysis.sh"]
    restart: unless-stopped
```

## Security Considerations

### Running as Non-root

```dockerfile
# Create non-root user
RUN useradd -m -u 1000 k8stools
USER k8stools
```

### Read-only Filesystem

```bash
docker run --rm \
  --read-only \
  -v ~/.kube:/root/.kube:ro \
  -v $(pwd)/tmp:/tmp \
  k8s-tools analyze
```

### Security Scanning

```bash
# Scan image for vulnerabilities
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image k8s-tools:latest
```

## Performance Optimization

### Resource Limits

```yaml
services:
  k8s-analyzer:
    image: k8stools/k8s-tools:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Caching

```dockerfile
# Use build cache
FROM python:3.11-slim

# Cache dependencies separately
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Copy source code last
COPY src/ src/
```

## Troubleshooting

### Common Issues

#### Permission Errors

```bash
# Fix ownership issues
docker run --rm \
  --user $(id -u):$(id -g) \
  -v ~/.kube:/root/.kube:ro \
  k8s-tools analyze
```

#### Network Access

```bash
# Use host networking for cluster access
docker run --rm \
  --network host \
  -v ~/.kube:/root/.kube:ro \
  k8s-tools analyze
```

### Debugging

```bash
# Run with debug output
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -v ~/.kube:/root/.kube:ro \
  k8s-tools analyze --verbose

# Interactive debugging
docker run -it --rm \
  -v ~/.kube:/root/.kube:ro \
  k8s-tools bash
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/analysis.yml
name: Cluster Analysis

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run K8s Analysis
        run: |
          docker run --rm \
            -v ${{ github.workspace }}/reports:/app/reports \
            -e KUBECONFIG_DATA="${{ secrets.KUBECONFIG }}" \
            k8stools/k8s-tools:latest \
            sh -c 'echo "$KUBECONFIG_DATA" > /tmp/kubeconfig && k8s-analyzer analyze --kubeconfig /tmp/kubeconfig'
      
      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: cluster-reports
          path: reports/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Cluster Analysis') {
            steps {
                sh '''
                    docker run --rm \
                        -v "${WORKSPACE}/reports:/app/reports" \
                        -v ~/.kube:/root/.kube:ro \
                        k8stools/k8s-tools:latest analyze
                '''
            }
        }
        
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/**/*'
            }
        }
    }
}
```

## Best Practices

### Image Management

1. **Use specific tags** instead of `latest` in production
2. **Implement health checks** for long-running containers
3. **Keep images small** using multi-stage builds
4. **Scan for vulnerabilities** regularly
5. **Use distroless images** when possible

### Configuration Management

1. **Use environment variables** for runtime configuration
2. **Mount configuration files** as read-only volumes
3. **Validate configuration** before running analysis
4. **Store sensitive data** in secrets management systems

### Monitoring

```bash
# Container health check
docker run --rm \
  --health-cmd="k8s-analyzer --version" \
  --health-interval=30s \
  k8s-tools analyze
```

## Related Documentation

- [Installation Guide](installation.md)
- [Kubernetes Deployment](kubernetes.md)
- [CI/CD Integration](cicd.md)

<citations>
<document>
<document_type>RULE</document_type>
<document_id>9aelDXM62tUDmHUQUL8XlE</document_id>
</document>
<document>
<document_type>RULE</document_type>
<document_id>mHRxidOov0WLb90jeiS2uG</document_id>
</document>
</citations>
