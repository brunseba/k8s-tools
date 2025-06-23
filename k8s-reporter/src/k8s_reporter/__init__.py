"""
K8s Reporter - Web UI for analyzing Kubernetes cluster data.

This package provides a Streamlit-based web interface for analyzing
Kubernetes cluster data exported by k8s-analyzer to SQLite databases.
"""

__version__ = "0.1.0"
__author__ = "K8s Reporter Team"

from .database import DatabaseClient
from .models import ClusterOverview, ResourceSummary, NamespaceAnalysis

__all__ = [
    "DatabaseClient",
    "ClusterOverview", 
    "ResourceSummary",
    "NamespaceAnalysis",
]
