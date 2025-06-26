# 💻 Development Setup

This guide covers setting up a development environment for contributing to K8s Tools, including both k8s-analyzer and k8s-reporter components.

## Prerequisites

Before starting development, ensure you have:

- **Python 3.9+** installed
- **Git** for version control
- **UV package manager** (recommended)
- **Node.js** (for frontend tooling, if needed)
- **Docker** (for testing containerized deployments)

## Development Environment Setup

### 1. Clone the Repository

```bash
# Clone the main repository
git clone https://github.com/k8s-tools/k8s-tools.git
cd k8s-tools

# Create your development branch
git checkout -b feature/your-feature-name
```

### 2. Install UV Package Manager

```bash
# Install UV (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using Homebrew (macOS)
brew install uv

# Or using pip
pip install uv
```

### 3. Setup k8s-analyzer Development

```bash
# Navigate to k8s-analyzer directory
cd k8s-analyzer

# Install dependencies with development extras
uv sync --all-extras

# Verify installation
uv run k8s-analyzer --help

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/k8s_analyzer --cov-report=html
```

### 4. Setup k8s-reporter Development

```bash
# Navigate to k8s-reporter directory
cd ../k8s-reporter

# Install dependencies with development extras
uv sync --all-extras

# Verify installation
uv run streamlit run src/k8s_reporter/app.py

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/k8s_reporter --cov-report=html
```

## Project Structure

```
k8s-tools/
├── k8s-analyzer/           # CLI analysis tool
│   ├── src/k8s_analyzer/   # Source code
│   ├── tests/              # Test suite
│   ├── docs/               # Component documentation
│   └── pyproject.toml      # Project configuration
├── k8s-reporter/           # Web dashboard
│   ├── src/k8s_reporter/   # Source code
│   ├── tests/              # Test suite
│   ├── docs/               # Component documentation
│   └── pyproject.toml      # Project configuration
├── docs/                   # Global documentation
├── examples/               # Usage examples
├── Taskfile.yml           # Task automation
├── mkdocs.yml             # Documentation configuration
└── README.md              # Main project README
```

## Development Workflow

### Code Quality Standards

Both projects use strict code quality standards:

```bash
# Format code with Black
uv run black src tests

# Sort imports with isort
uv run isort src tests

# Lint code with flake8
uv run flake8 src tests

# Type checking with mypy
uv run mypy src

# Run all quality checks
uv run pre-commit run --all-files
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
```

### Testing

#### k8s-analyzer Tests

```bash
cd k8s-analyzer

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_parser.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/k8s_analyzer --cov-report=term-missing
```

#### k8s-reporter Tests

```bash
cd k8s-reporter

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_database.py

# Run with coverage
uv run pytest --cov=src/k8s_reporter --cov-report=html
```

### Creating Test Data

For development and testing, you can generate test data:

```bash
# Generate test cluster data
kubectl create namespace test-namespace
kubectl create deployment test-app --image=nginx -n test-namespace
kubectl get all,pv,pvc,configmaps -n test-namespace -o json > test-data.json

# Use the test data
cd k8s-analyzer
uv run k8s-analyzer sqlite ../test-data.json --output test.db

cd ../k8s-reporter
uv run streamlit run src/k8s_reporter/app.py
```

## Making Changes

### Adding New Features to k8s-analyzer

1. **Create new module** in `src/k8s_analyzer/`
2. **Add tests** in `tests/`
3. **Update CLI** in `cli.py` if needed
4. **Add documentation** in appropriate docs

Example:
```python
# src/k8s_analyzer/new_feature.py
def new_analysis_function(cluster_state):
    """New analysis functionality."""
    # Implementation here
    pass

# tests/test_new_feature.py
def test_new_analysis_function():
    """Test the new analysis function."""
    # Test implementation
    pass
```

### Adding New Views to k8s-reporter

1. **Create view module** in `src/k8s_reporter/views/`
2. **Add to views registry** in `models.py`
3. **Add tests** in `tests/`
4. **Update navigation** in `app.py`

Example:
```python
# src/k8s_reporter/views/new_view.py
import streamlit as st

def render_new_view(db_client, filters):
    """Render the new analysis view."""
    st.header("New Analysis View")
    # Implementation here

# src/k8s_reporter/models.py
ANALYSIS_VIEWS = {
    # ... existing views
    "new_view": AnalysisView(
        title="New View",
        icon="📊",
        render_func=render_new_view,
    )
}
```

### Database Schema Changes

If you need to modify the database schema:

1. **Update models** in `k8s-analyzer/src/k8s_analyzer/models.py`
2. **Update SQLite exporter** in `sqlite_exporter.py`
3. **Update database client** in `k8s-reporter/src/k8s_reporter/database.py`
4. **Add migration logic** if needed
5. **Update tests** for all components

## Testing Your Changes

### Integration Testing

```bash
# Test full workflow
cd k8s-analyzer
uv run k8s-analyzer sqlite ../examples/multi-app-demo/ --output integration-test.db

cd ../k8s-reporter
uv run streamlit run src/k8s_reporter/app.py
# Upload the integration-test.db and verify functionality
```

### Performance Testing

```bash
# Test with large datasets
kubectl get all,pv,pvc,configmaps,secrets -A -o json > large-cluster.json

cd k8s-analyzer
time uv run k8s-analyzer sqlite large-cluster.json --output large-test.db

cd ../k8s-reporter
# Test dashboard performance with large database
```

## Documentation

### Updating Documentation

1. **Component docs**: Update READMEs in component directories
2. **Global docs**: Update files in `docs/` directory
3. **API docs**: Update docstrings in code
4. **Examples**: Update examples in `examples/` directory

### Building Documentation

```bash
# Install mkdocs
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Debugging

### Debugging k8s-analyzer

```bash
# Enable verbose logging
uv run k8s-analyzer analyze test-data.json --verbose

# Use Python debugger
uv run python -m pdb -c continue src/k8s_analyzer/cli.py analyze test-data.json
```

### Debugging k8s-reporter

```bash
# Enable debug mode
uv run streamlit run src/k8s_reporter/app.py --logger.level=debug

# Use browser developer tools for frontend issues
```

## CI/CD Integration

### GitHub Actions

The project uses GitHub Actions for CI/CD:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
      - uses: actions/checkout@v3
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Test k8s-analyzer
        run: |
          cd k8s-analyzer
          uv sync --all-extras
          uv run pytest
      - name: Test k8s-reporter
        run: |
          cd k8s-reporter
          uv sync --all-extras
          uv run pytest
```

### Local CI Testing

```bash
# Install act (GitHub Actions local runner)
brew install act

# Run tests locally
act -j test
```

## Release Process

### Version Management

1. **Update version** in `pyproject.toml` files
2. **Update CHANGELOG.md** with new features and fixes
3. **Create git tag** with version number
4. **Push changes** and tag to GitHub

```bash
# Update versions
# Edit k8s-analyzer/pyproject.toml
# Edit k8s-reporter/pyproject.toml
# Edit CHANGELOG.md

# Commit changes
git add .
git commit -m "Release v1.0.0"

# Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags
```

### Using Taskfile for Releases

```bash
# Install Task
brew install go-task/tap/go-task

# View available tasks
task --list

# Create release
task create-release
```

## Contributing Guidelines

### Pull Request Process

1. **Fork** the repository
2. **Create feature branch** from `main`
3. **Make changes** following code quality standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit pull request** with clear description

### Code Review Checklist

- [ ] Code follows style guidelines (Black, isort, flake8)
- [ ] Tests pass and cover new functionality
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact is considered
- [ ] Security implications are addressed

### Community Guidelines

- Be respectful and inclusive
- Follow the code of conduct
- Help others learn and contribute
- Report issues constructively
- Share knowledge and best practices

## Getting Help

### Development Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Comprehensive guides and examples
- **Code Examples**: Reference implementations

### Resources

- **Python Documentation**: [https://docs.python.org/](https://docs.python.org/)
- **Streamlit Documentation**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Plotly Documentation**: [https://plotly.com/python/](https://plotly.com/python/)
- **Kubernetes API Reference**: [https://kubernetes.io/docs/reference/](https://kubernetes.io/docs/reference/)

## Performance Optimization

### Development Tips

- Use caching for expensive operations
- Implement lazy loading for large datasets
- Profile code performance regularly
- Optimize database queries
- Use efficient data structures

### Memory Management

```python
# Use generators for large datasets
def process_resources(resources):
    for resource in resources:
        yield analyze_resource(resource)

# Cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_analysis(resource_id):
    # Expensive computation here
    pass
```

This development setup guide provides everything needed to contribute effectively to the K8s Tools project. Follow the guidelines, maintain code quality, and help build better tools for the Kubernetes community!
