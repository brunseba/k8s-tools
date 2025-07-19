# Testing

Comprehensive testing is essential for maintaining code quality and reliability in K8s Tools. This guide covers our testing strategy, tools, and best practices.

## Testing Strategy

### Test Pyramid

Our testing approach follows the test pyramid:

1. **Unit Tests** (Base): Fast, isolated tests for individual components
2. **Integration Tests** (Middle): Tests for component interactions
3. **End-to-End Tests** (Top): Full workflow tests

### Test Categories

- **Unit Tests**: Core business logic, utilities, and data models
- **Integration Tests**: Database operations, API integrations, CLI commands
- **End-to-End Tests**: Complete user workflows and scenarios
- **Performance Tests**: Load testing and benchmarking
- **Security Tests**: Vulnerability scanning and security validation

## Test Tools and Framework

### Primary Testing Framework

We use **pytest** as our primary testing framework:

```bash
# Install testing dependencies
uv sync --group test

# Run all tests
pytest

# Run with coverage reporting
pytest --cov=src --cov-report=html --cov-report=term
```

### Testing Dependencies

```toml
# pyproject.toml testing dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.10",
    "pytest-asyncio>=0.21",
    "pytest-xdist>=3.0",  # for parallel test execution
    "factory-boy>=3.2",   # for test data factories
    "freezegun>=1.2",     # for time-based testing
    "responses>=0.23",    # for HTTP mocking
]
```

## Test Structure and Organization

### Directory Structure

```
tests/
├── unit/
│   ├── analyzer/
│   │   ├── test_core.py
│   │   ├── test_metrics.py
│   │   └── test_views.py
│   ├── reporter/
│   │   ├── test_dashboard.py
│   │   └── test_exporters.py
│   └── common/
│       ├── test_utils.py
│       └── test_models.py
├── integration/
│   ├── test_cli.py
│   ├── test_database.py
│   └── test_k8s_client.py
├── e2e/
│   ├── test_full_analysis.py
│   └── test_reporting_workflow.py
├── fixtures/
│   ├── kubernetes/
│   │   ├── pods.yaml
│   │   └── deployments.yaml
│   └── sample_data/
└── conftest.py
```

### Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_<functionality>_<expected_result>()`
- Test classes: `Test<ComponentName>`

```python
# Good examples
def test_cluster_analyzer_returns_node_metrics():
    pass

def test_security_analysis_identifies_vulnerabilities():
    pass

class TestDashboardGenerator:
    def test_generate_html_dashboard_with_valid_data(self):
        pass
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from k8s_tools.analyzer.core import ClusterAnalyzer
from k8s_tools.common.models import ClusterMetrics

class TestClusterAnalyzer:
    """Test cases for ClusterAnalyzer class."""
    
    @pytest.fixture
    def mock_k8s_client(self):
        """Mock Kubernetes client for testing."""
        return Mock()
    
    @pytest.fixture
    def analyzer(self, mock_k8s_client):
        """Create analyzer instance with mocked dependencies."""
        return ClusterAnalyzer(client=mock_k8s_client)
    
    def test_analyze_cluster_returns_metrics(self, analyzer, mock_k8s_client):
        """Test that analyze_cluster returns ClusterMetrics object."""
        # Arrange
        mock_k8s_client.list_nodes.return_value = []
        mock_k8s_client.list_pods.return_value = []
        
        # Act
        result = analyzer.analyze_cluster()
        
        # Assert
        assert isinstance(result, ClusterMetrics)
        assert result.node_count >= 0
        mock_k8s_client.list_nodes.assert_called_once()
    
    def test_analyze_cluster_handles_api_error(self, analyzer, mock_k8s_client):
        """Test error handling when Kubernetes API fails."""
        # Arrange
        mock_k8s_client.list_nodes.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            analyzer.analyze_cluster()
```

### Integration Test Example

```python
import pytest
from click.testing import CliRunner
from k8s_tools.cli.main import cli

class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Click test runner."""
        return CliRunner()
    
    def test_analyze_command_with_valid_config(self, runner, temp_config_file):
        """Test analyze command with valid configuration."""
        result = runner.invoke(cli, [
            'analyze', 
            '--config', temp_config_file,
            '--view', 'cluster-overview'
        ])
        
        assert result.exit_code == 0
        assert "Cluster Analysis Complete" in result.output
    
    @pytest.mark.skipif(not pytest.k8s_available, reason="K8s cluster not available")
    def test_analyze_against_real_cluster(self, runner):
        """Test against real Kubernetes cluster (requires cluster access)."""
        result = runner.invoke(cli, ['analyze', '--view', 'health-dashboard'])
        assert result.exit_code == 0
```

### Test Fixtures and Factories

```python
# conftest.py
import pytest
import tempfile
import yaml
from pathlib import Path

@pytest.fixture
def sample_pod_data():
    """Sample Kubernetes pod data for testing."""
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "test-pod",
            "namespace": "default",
        },
        "spec": {
            "containers": [
                {
                    "name": "test-container",
                    "image": "nginx:latest",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"cpu": "500m", "memory": "512Mi"}
                    }
                }
            ]
        }
    }

@pytest.fixture
def temp_config_file():
    """Create temporary configuration file for testing."""
    config_data = {
        "cluster": {"name": "test-cluster"},
        "analysis": {"views": ["cluster-overview"]},
        "output": {"format": "json"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        yield f.name
    
    Path(f.name).unlink()  # cleanup
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/analyzer/test_core.py

# Run specific test function
pytest tests/unit/analyzer/test_core.py::test_analyze_cluster_returns_metrics

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Set minimum coverage threshold
pytest --cov=src --cov-fail-under=80
```

### Test Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_comprehensive_cluster_analysis():
    pass

# Mark tests requiring Kubernetes
@pytest.mark.k8s
def test_real_cluster_connection():
    pass

# Mark integration tests
@pytest.mark.integration
def test_database_operations():
    pass
```

Run specific test groups:
```bash
# Run only unit tests (default)
pytest tests/unit/

# Run integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run only Kubernetes tests
pytest -m k8s
```

## Test Data Management

### Test Data Files

Store test data in `tests/fixtures/`:

```yaml
# tests/fixtures/kubernetes/sample-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
    spec:
      containers:
      - name: app
        image: nginx:1.20
```

### Factory Pattern for Test Data

```python
# tests/factories.py
import factory
from k8s_tools.common.models import NodeMetrics, PodMetrics

class NodeMetricsFactory(factory.Factory):
    class Meta:
        model = NodeMetrics
    
    name = factory.Sequence(lambda n: f"node-{n}")
    cpu_capacity = "4"
    memory_capacity = "8Gi"
    cpu_usage = factory.LazyAttribute(lambda obj: obj.cpu_capacity * 0.5)
    memory_usage = factory.LazyAttribute(lambda obj: obj.memory_capacity * 0.6)

# Usage in tests
def test_node_metrics_calculation():
    node = NodeMetricsFactory()
    assert node.cpu_usage_percentage < 100
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Install dependencies
      run: uv sync --group test
    
    - name: Run tests
      run: uv run pytest --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## Best Practices

### Test Writing Guidelines

1. **Arrange-Act-Assert**: Structure tests clearly
2. **Single Responsibility**: One test, one behavior
3. **Descriptive Names**: Test names should describe the scenario
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Execution**: Keep unit tests fast (< 1 second each)

### Mocking Guidelines

```python
# Good: Mock external dependencies
@patch('k8s_tools.client.kubernetes_client')
def test_analysis_with_mocked_client(mock_client):
    pass

# Good: Use pytest-mock for cleaner syntax
def test_analysis_with_mocker(mocker):
    mock_client = mocker.patch('k8s_tools.client.kubernetes_client')
    pass

# Avoid: Over-mocking internal logic
# Don't mock what you're testing
```

### Performance Testing

```python
import pytest
import time

def test_analysis_performance():
    """Test that cluster analysis completes within acceptable time."""
    start_time = time.time()
    
    # Perform analysis
    result = analyzer.analyze_cluster()
    
    execution_time = time.time() - start_time
    assert execution_time < 5.0  # Should complete within 5 seconds
```

## Related Documentation

- [Development Setup](setup.md)
- [Contributing Guidelines](contributing.md)
- [Architecture Overview](architecture.md)

<citations>
<document>
<document_type>RULE</document_type>
<document_id>mHRxidOov0WLb90jeiS2uG</document_id>
</document>
</citations>
