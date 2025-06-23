"""
Data models for k8s-reporter.

These models define the structure for various analysis views and reports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ResourceSummary(BaseModel):
    """Summary of resource counts and health status."""
    
    total_resources: int
    total_relationships: int
    health_distribution: Dict[str, int]
    resource_types: Dict[str, int]
    namespaces_count: int
    issues_count: int


class NamespaceAnalysis(BaseModel):
    """Analysis of a specific namespace."""
    
    name: str
    resource_count: int
    resource_types: Dict[str, int]
    health_distribution: Dict[str, int]
    issues_count: int
    relationships_count: int
    top_resources: List[Dict[str, str]]


class ClusterOverview(BaseModel):
    """High-level cluster overview."""
    
    cluster_name: Optional[str] = None
    analysis_timestamp: datetime
    total_resources: int
    total_namespaces: int
    health_ratio: float  # Percentage of healthy resources
    top_namespaces: List[Dict[str, int]]
    resource_distribution: Dict[str, int]
    issues_summary: Dict[str, int]


class SecurityAnalysis(BaseModel):
    """Security-focused analysis of the cluster."""
    
    privileged_pods: int
    pods_without_security_context: int
    root_containers: int
    service_accounts_count: int
    role_bindings_count: int
    cluster_role_bindings: int
    secrets_count: int
    config_maps_count: int


class ResourceEfficiency(BaseModel):
    """Resource efficiency and optimization insights."""
    
    pods_without_limits: int
    pods_without_requests: int
    over_requested_resources: List[Dict[str, str]]
    unused_config_maps: int
    orphaned_pvcs: int
    services_without_endpoints: int


class ComplianceReport(BaseModel):
    """Compliance and best practices report."""
    
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    compliance_score: float  # Percentage
    failed_policies: List[Dict[str, str]]
    recommendations: List[str]


@dataclass
class ViewConfig:
    """Configuration for different analysis views."""
    
    title: str
    description: str
    icon: str
    requires_namespace_filter: bool = False
    supports_time_range: bool = False


class AnalysisView:
    """Base class for different analysis views."""
    
    def __init__(self, name: str, config: ViewConfig):
        self.name = name
        self.config = config
    
    def get_title(self) -> str:
        return f"{self.config.icon} {self.config.title}"
    
    def get_description(self) -> str:
        return self.config.description


# Predefined analysis views
ANALYSIS_VIEWS = {
    "overview": AnalysisView(
        "overview",
        ViewConfig(
            title="Cluster Overview",
            description="High-level cluster health and resource distribution",
            icon="🏠",
        )
    ),
    "security": AnalysisView(
        "security", 
        ViewConfig(
            title="Security Analysis",
            description="Security posture and RBAC analysis",
            icon="🔒",
        )
    ),
    "efficiency": AnalysisView(
        "efficiency",
        ViewConfig(
            title="Resource Efficiency", 
            description="Resource utilization and optimization opportunities",
            icon="⚡",
        )
    ),
    "compliance": AnalysisView(
        "compliance",
        ViewConfig(
            title="Compliance Report",
            description="Best practices and policy compliance",
            icon="✅",
        )
    ),
    "namespaces": AnalysisView(
        "namespaces",
        ViewConfig(
            title="Namespace Analysis",
            description="Per-namespace resource breakdown and health",
            icon="🏷️",
            requires_namespace_filter=True,
        )
    ),
    "relationships": AnalysisView(
        "relationships",
        ViewConfig(
            title="Resource Relationships",
            description="Resource dependencies and interconnections",
            icon="🔗",
        )
    ),
    "health": AnalysisView(
        "health",
        ViewConfig(
            title="Health Dashboard",
            description="Resource health status and issues tracking",
            icon="❤️",
        )
    ),
    "trends": AnalysisView(
        "trends",
        ViewConfig(
            title="Trends Analysis",
            description="Historical trends and changes over time",
            icon="📈",
            supports_time_range=True,
        )
    ),
}
