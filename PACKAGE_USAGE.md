# Package Usage from GitHub Releases

This repository publishes Python wheel packages to GitHub Releases instead of PyPI. Here's how to install and use them:

## Installation Options

### Option 1: Install from GitHub Releases (Recommended)

1. **Download the latest release:**
   - Go to the [Releases page](https://github.com/brunseba/k8s-tools/releases)
   - Find the latest release for your desired package (`k8s-analyzer` or `k8s-reporter`)
   - Download the `.whl` file for your package

2. **Install the downloaded wheel:**
   ```bash
   pip install path/to/downloaded/package.whl
   ```

### Option 2: Install directly from GitHub

```bash
# For k8s-analyzer
pip install https://github.com/brunseba/k8s-tools/releases/download/k8s-analyzer-v0.7.3/k8s_analyzer-0.7.3-py3-none-any.whl

# For k8s-reporter  
pip install https://github.com/brunseba/k8s-tools/releases/download/k8s-reporter-v0.7.9/k8s_reporter-0.7.9-py3-none-any.whl
```

### Option 3: Install from source

```bash
git clone https://github.com/brunseba/k8s-tools.git
cd k8s-tools

# Install k8s-analyzer
cd k8s-analyzer
pip install -e .

# Install k8s-reporter
cd ../k8s-reporter
pip install -e .
```

## Available Packages

### k8s-analyzer
- **Purpose**: Kubernetes resource analyzer with relationship mapping
- **Python Requirements**: ≥3.11
- **Command**: `k8s-analyzer`

### k8s-reporter  
- **Purpose**: Web UI for analyzing Kubernetes cluster data
- **Python Requirements**: ≥3.9
- **Command**: `k8s-reporter`

## CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. **Tests**: Runs pytest with coverage on multiple Python versions
2. **SBOM Generation**: Creates Software Bill of Materials for security
3. **Package Building**: Builds both wheel and source distributions
4. **Releases**: Creates GitHub releases with:
   - Wheel packages (`.whl`)
   - Source distributions (`.tar.gz`)
   - SBOM files (`.json`)
   - Auto-generated release notes

## Package Versioning

- Packages are tagged as `{package-name}-v{version}`
- Example: `k8s-analyzer-v0.7.3`, `k8s-reporter-v0.7.9`
- Version numbers are automatically extracted from `pyproject.toml`

## Security

- All packages include SBOM (Software Bill of Materials) files
- Dependencies are tracked and published with each release
- Packages are built in isolated GitHub Actions environments
