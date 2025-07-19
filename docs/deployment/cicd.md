# CI/CD Integration

This guide covers integrating K8s Tools into continuous integration and continuous deployment (CI/CD) pipelines using GitHub Actions, Jenkins, and GitLab CI.

## Overview

CI/CD integration provides:

- **Automation**: Streamlined workflows from code commit to deployment
- **Consistency**: Reproducible environments and deployments
- **Monitoring and Feedback**: Real-time insights through automated tests and reports

## GitHub Actions

### Setting Up GitHub Actions

Create a workflow file in `.github/workflows/ci.yml`:

```yaml
name: K8s Tools CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install Dependencies
      run: |
        pip install uv
        uv sync --dev
    - name: Run Tests
      run: |
        pytest --cov=.

  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
    - name: Deploy to K8s
      run: |
        kubectl apply -f k8s-tools-deployment.yaml
```

### Triggers and Conditions

- **Push**: Run on every push to main
- **Pull Request**: Validate changes in PRs
- **Scheduled**: Use cron for scheduled runs

## Jenkins Pipeline

### Creating a Jenkinsfile

Create `Jenkinsfile` in the root of your repository:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'uv sync --dev'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest --cov=.'
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f k8s-tools-deployment.yaml'
            }
        }
    }
    post {
        success {
            echo 'Pipeline successfully completed.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
```

### Configuring Jenkins

1. **Install Plugins**: GitHub, Kubernetes CLI
2. **Configure Credentials**: Setup kubeconfig for deployment
3. **Create Pipelines**: Use the Jenkinsfile above

## GitLab CI/CD

### Example .gitlab-ci.yml

Create `.gitlab-ci.yml` in the root of your repository:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  KUBECONFIG: /kube/config

build:
  stage: build
  image: python:3.11
  script:
    - pip install uv
    - uv sync --dev

unit_tests:
  stage: test
  image: python:3.11
  script:
    - pytest --cov=.

deploy:
  stage: deploy
  image: registry.gitlab.com/gitlab-org/cloud-build
  script:
    - kubectl apply -f k8s-tools-deployment.yaml
```

## Environment Management

### Secrets Management

- **GitHub Secrets**: Manage sensitive data in GitHub Actions
- **Jenkins Credentials**: Securely store kubeconfig and other secrets
- **GitLab Variables**: Store environment-specific configurations

### Dependency Management

Use dependency management tools to ensure reproducibility:

- **pipx**: Isolated Python version management
- **uv**: Fast and consistent dependency installation

## Monitoring and Alerts

### Real-Time Monitoring

Integrate with monitoring solutions to track deployment status:

- **Prometheus/Grafana**: Visualize deployment metrics
- **Slack Notifications**: Receive alerts via Slack for build/deployments

### Status Dashboards

Create custom dashboards in Jenkins and GitLab to report CI/CD status:

- **Build Status**: Track latest build state
- **Test Coverage**: Ensure sufficient test coverage
- **Deployment Success**: Confirm successful deployments

## Best Practices

1. **Reusable Workflows**: Modularize CI/CD scripts
2. **Parallel Stages**: Optimize build/test times
3. **Rollback Plans**: Prepare for easy rollback in deployments
4. **Continuous Improvement**: Keep pipelines updated

## Related Documentation

- [Setup Guide](../setup.md)
- [Kubernetes Deployment](kubernetes.md)
- [Docker Deployment](docker.md)
