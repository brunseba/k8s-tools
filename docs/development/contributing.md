# Contributing

Thank you for your interest in contributing to K8s Tools! This guide will help you get started with development and contributions.

## Development Setup

Before you begin, ensure you have completed the [development setup](setup.md).

## Contributing Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please read and follow our Code of Conduct.

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/k8s-tools.git
   cd k8s-tools
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Process

#### Setting up Development Environment

```bash
# Install dependencies with uv
uv sync --dev

# Activate the virtual environment
source .venv/bin/activate

# Install pre-commit hooks
pre-commit install
```

#### Code Standards

- **Python Version**: >= 3.10 (as per project rules)
- **Code Style**: Follow PEP 8, enforced by pre-commit hooks
- **Type Hints**: Use type hints for all functions and methods
- **Documentation**: Document all public APIs and functions

#### Commit Guidelines

We use conventional commits for consistent commit messages:

```bash
# Format: type(scope): description
feat(analyzer): add new cluster analysis view
fix(reporter): resolve dashboard rendering issue
docs(api): update CLI reference documentation
test(core): add unit tests for data models
```

**Commit Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation updates
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py

# Run tests with verbose output
pytest -v
```

#### Writing Tests

- Write unit tests for all new functionality
- Place tests in the `tests/` directory
- Follow the naming convention: `test_*.py`
- Use descriptive test names

```python
def test_cluster_analysis_returns_valid_data():
    """Test that cluster analysis returns properly formatted data."""
    # Test implementation
    pass
```

### Documentation

#### Building Documentation

```bash
# Install MkDocs dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

#### Documentation Guidelines

- Update relevant documentation when making changes
- Use clear, concise language
- Include code examples where appropriate
- Update API documentation for new features

### Pull Request Process

1. **Create a Pull Request** from your feature branch to `main`
2. **Fill out the PR template** with:
   - Description of changes
   - Type of change (bug fix, feature, docs, etc.)
   - Testing performed
   - Breaking changes (if any)
3. **Ensure CI passes** - all tests and checks must pass
4. **Request review** from maintainers
5. **Address feedback** and update your PR as needed

#### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Tests added for new functionality
- [ ] Documentation updated as needed
- [ ] Changelog updated (if applicable)
- [ ] PR title follows conventional commit format

### Release Process

Releases are managed by maintainers and follow semantic versioning:

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, backwards compatible

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord/Slack**: [Community channel link if available]

### Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- Documentation credits

Thank you for contributing to K8s Tools! 🎉
