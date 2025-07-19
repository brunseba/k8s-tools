# Installation

This document provides detailed instructions for installing K8s Tools, including system requirements, installation steps, and initial setup guidelines.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python Version**: >= 3.10
- **Kubernetes Cluster**: Version >= 1.21 (for Kubernetes resources)
- **Access**: Ability to access the Kubernetes API server

## Installation Options

### Using pipx

We recommend using **pipx** for isolated installations. If pipx is not installed, you can install it first:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

To install K8s Tools using pipx:

```bash
pipx install k8s-tools
```

### Using pip

Alternatively, you can install K8s Tools directly with pip:

```bash
pip install k8s-tools
```

### From Source

To install from source, clone the repository and install using pip:

```bash
git clone https://github.com/k8s-tools/k8s-tools.git
cd k8s-tools
pip install .
```

### Using Docker

K8s Tools can also be run in a Docker container:

```bash
# Pull Docker image
docker pull k8stools/k8s-tools

# Run container
docker run -it --rm -v ~/.kube:/home/user/.kube k8stools/k8s-tools analyze
```

## Setup and Configuration

### Kubernetes Configuration

Ensure that your `kubeconfig` is set up correctly:

- By default, K8s Tools uses the kubeconfig located at `~/.kube/config`
- You can specify a different kubeconfig path with the `--kubeconfig` option:

```bash
k8s-tools analyze --kubeconfig /path/to/config
```

### Environment Variables

You may set environment variables to customize behavior:

- `K8S_TOOLS_CONFIG` - Path to the configuration file
- `KUBECONFIG` - Override kubeconfig location

### Pre-Commit Hooks

Set up pre-commit hooks for development:

```bash
pre-commit install
```

### Initial Testing

Run initial tests to verify installation:

```bash
# Run unit tests
pytest
test/test_initialization.py

# Check version
k8s-tools --version
```

## Troubleshooting

### Common Issues

- **Dependency Resolution**: Conflicts with existing packages
  - Use `pip check` to identify conflicts

- **Kubeconfig Errors**: Issues with Kubernetes configuration
  - Ensure the correct context is set in kubeconfig

### Getting Help

- **Documentation**: Refer to detailed usage guides and examples
- **Community Support**: Reach out via GitHub issues or discussions

### Uninstallation

To remove K8s Tools:

```bash
pipx uninstall k8s-tools
# or if installed with pip
pip uninstall k8s-tools
```

## Related Resources

- [Quick Start Guide](getting-started.md)
- [Changelog](CHANGELOG.md)
- [Usage Examples](examples/basic-usage.md)

0citations1
0document1
0document_type1RULE0/document_type1
0document_id1mHRxidOov0WLb90jeiS2uG0/document_id1
0/document1
0document1
0document_type1RULE0/document_type1
0document_id1FtUk1rgWdKE6veAClNpAqC0/document_id1
0/document1
0/citations1
