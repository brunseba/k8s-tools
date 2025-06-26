"""
Data models for k8s-reporter.

These models define the structure for various analysis views and reports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

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


class NamespaceComponent(BaseModel):
    """Individual component within a namespace."""
    
    name: str
    kind: str
    health_status: str
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}
    issues: List[str] = []
    created_at: Optional[str] = None
    

class NamespaceRelationship(BaseModel):
    """Relationship between components in a namespace."""
    
    source_name: str
    source_kind: str
    target_name: str
    target_kind: str
    relationship_type: str
    strength: float = 1.0
    description: Optional[str] = None


class NamespaceComponentsView(BaseModel):
    """Detailed view of namespace components and their relationships."""
    
    namespace: str
    total_components: int
    components: List[NamespaceComponent]
    relationships: List[NamespaceRelationship]
    component_groups: Dict[str, List[str]]  # Group components by type
    dependency_chains: List[List[str]]  # Ordered dependency chains
    orphaned_components: List[str]  # Components with no relationships
    critical_components: List[str]  # Components with many relationships


class ClusterOverview(BaseModel):
    """High-level cluster overview."""
    
    cluster_name: Optional[str] = None
    analysis_timestamp: datetime
    total_resources: int
    total_namespaces: int
    health_ratio: float  # Percentage of healthy resources
    top_namespaces: List[Dict[str, Union[str, int]]]  # Allow both str and int values
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


class PodResourceIssue(BaseModel):
    """Pod with resource configuration issues."""
    
    name: str
    namespace: str
    containers: List[str]
    missing_requests: List[str]  # cpu, memory
    missing_limits: List[str]   # cpu, memory
    health_status: str
    created_at: Optional[datetime] = None
    node: Optional[str] = None
    issue_severity: str  # low, medium, high, critical
    recommendations: List[str] = []


class ResourceEfficiency(BaseModel):
    """Resource efficiency and optimization insights."""
    
    pods_without_limits: int
    pods_without_requests: int
    pods_without_any_resources: int  # No requests AND no limits
    pods_with_partial_resources: int  # Some containers missing resources
    over_requested_resources: List[Dict[str, str]]
    unused_config_maps: int
    orphaned_pvcs: int
    services_without_endpoints: int
    problematic_pods: List[PodResourceIssue]
    resource_coverage_percentage: float
    total_pods_analyzed: int


class ComplianceReport(BaseModel):
    """Compliance and best practices report."""
    
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    compliance_score: float  # Percentage
    failed_policies: List[Dict[str, str]]
    recommendations: List[str]


class StorageVolume(BaseModel):
    """Individual storage volume information."""
    
    name: str
    namespace: Optional[str] = None
    kind: str  # PV, PVC, etc.
    capacity: Optional[str] = None
    storage_class: Optional[str] = None
    access_modes: List[str] = []
    status: str
    bound_to: Optional[str] = None  # For PVC -> PV binding
    created_at: Optional[datetime] = None
    labels: Dict[str, str] = {}


class StorageConsumption(BaseModel):
    """Storage consumption analysis."""
    
    total_volumes: int
    total_capacity_gb: float
    used_capacity_gb: float
    utilization_percentage: float
    volumes_by_class: Dict[str, int]
    capacity_by_class: Dict[str, float]
    volumes_by_status: Dict[str, int]
    unbound_pvcs: int
    orphaned_pvs: int
    top_consumers: List[StorageVolume]


class NamespaceStorageAnalysis(BaseModel):
    """Per-namespace storage analysis."""
    
    namespace: str
    total_volumes: int
    total_capacity_gb: float
    storage_classes: Dict[str, int]
    access_patterns: Dict[str, int]  # ReadWriteOnce, ReadOnlyMany, etc.
    volume_status: Dict[str, int]
    volumes: List[StorageVolume]
    largest_volumes: List[StorageVolume]


class ResourceTimeline(BaseModel):
    """Timeline data for resource lifecycle events."""
    
    resource_name: str
    resource_kind: str
    namespace: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    events: List[Dict[str, Any]] = []  # Timeline events
    age_days: float
    lifecycle_stage: str  # new, active, stale, etc.


class TemporalAnalysis(BaseModel):
    """Temporal analysis of cluster resources."""
    
    analysis_period: str  # Description of time period analyzed
    total_resources: int
    creation_timeline: List[Dict[str, Any]]  # Resources created over time
    update_timeline: List[Dict[str, Any]]  # Resources updated over time
    age_distribution: Dict[str, int]  # Resources by age groups
    most_active_namespaces: List[Dict[str, Union[str, int]]]
    newest_resources: List[ResourceTimeline]
    oldest_resources: List[ResourceTimeline]
    stale_resources: List[ResourceTimeline]  # Not updated recently
    creation_patterns: Dict[str, int]  # Creation by day of week, hour, etc.
    resource_lifecycle_stats: Dict[str, Dict[str, float]]  # Avg age by type


class LabelAnalysis(BaseModel):
    """Analysis of resources grouped by metadata labels."""
    
    total_labeled_resources: int
    total_unlabeled_resources: int
    label_coverage_percentage: float
    common_labels: Dict[str, int]  # label key -> count of resources with this label
    label_values_distribution: Dict[str, Dict[str, int]]  # label key -> {value -> count}
    resources_by_label: Dict[str, List[Dict[str, Any]]]  # label key -> list of resources
    orphaned_resources: List[Dict[str, Any]]  # resources without common organizational labels
    label_quality_score: float  # Overall labeling quality percentage


class ApplicationViewpoint(BaseModel):
    """Application-centric view based on app.kubernetes.io labels."""
    
    total_applications: int
    applications: List[Dict[str, Any]]  # app name -> details
    application_health: Dict[str, str]  # app name -> health status
    application_resources: Dict[str, List[Dict[str, Any]]]  # app name -> resources
    application_versions: Dict[str, str]  # app name -> version
    application_components: Dict[str, List[str]]  # app name -> component types
    orphaned_resources: List[Dict[str, Any]]  # resources without app labels
    multi_app_resources: List[Dict[str, Any]]  # resources belonging to multiple apps


class EnvironmentViewpoint(BaseModel):
    """Environment-based view using environment labels."""
    
    environments: List[str]  # detected environments (prod, staging, dev, etc.)
    resources_by_environment: Dict[str, int]  # env -> resource count
    environment_health: Dict[str, Dict[str, int]]  # env -> {health_status -> count}
    environment_namespaces: Dict[str, List[str]]  # env -> namespaces
    environment_applications: Dict[str, List[str]]  # env -> applications
    untagged_resources: List[Dict[str, Any]]  # resources without environment labels
    environment_compliance: Dict[str, float]  # env -> compliance percentage


class TeamOwnershipViewpoint(BaseModel):
    """Team/ownership view based on ownership labels."""
    
    teams: List[str]  # detected teams
    team_resources: Dict[str, int]  # team -> resource count
    team_namespaces: Dict[str, List[str]]  # team -> namespaces they own
    team_applications: Dict[str, List[str]]  # team -> applications they own
    unowned_resources: List[Dict[str, Any]]  # resources without ownership labels
    team_health_status: Dict[str, Dict[str, int]]  # team -> {health_status -> count}
    cross_team_dependencies: List[Dict[str, Any]]  # relationships across teams
    ownership_coverage: float  # percentage of resources with ownership labels


class CostOptimizationViewpoint(BaseModel):
    """Cost optimization view based on cost-related labels."""
    
    cost_centers: List[str]  # detected cost centers
    cost_center_resources: Dict[str, int]  # cost center -> resource count
    cost_center_storage: Dict[str, float]  # cost center -> storage consumption (GB)
    cost_center_namespaces: Dict[str, List[str]]  # cost center -> namespaces
    untagged_for_billing: List[Dict[str, Any]]  # resources missing cost/billing labels
    cost_optimization_opportunities: List[Dict[str, Any]]  # resources that could be optimized
    billing_coverage: float  # percentage of resources with cost/billing labels


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
    "namespace_components": AnalysisView(
        "namespace_components",
        ViewConfig(
            title="Namespace Components",
            description="Detailed per-namespace component analysis with relationships",
            icon="🏗️",
            requires_namespace_filter=False,  # We handle namespace selection internally
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
    "storage": AnalysisView(
        "storage",
        ViewConfig(
            title="Storage Analysis",
            description="Storage consumption and volume analysis",
            icon="💾",
        )
    ),
    "temporal": AnalysisView(
        "temporal",
        ViewConfig(
            title="Temporal Analysis",
            description="Resource lifecycle and creation patterns over time",
            icon="⏰",
            supports_time_range=True,
        )
    ),
    "labels": AnalysisView(
        "labels",
        ViewConfig(
            title="Label Analysis",
            description="Resource organization and labeling patterns",
            icon="🏷️",
        )
    ),
    "applications": AnalysisView(
        "applications",
        ViewConfig(
            title="Application View",
            description="Application-centric analysis based on app.kubernetes.io labels",
            icon="🚀",
        )
    ),
    "environments": AnalysisView(
        "environments",
        ViewConfig(
            title="Environment View",
            description="Environment-based resource organization and health",
            icon="🌍",
        )
    ),
    "team_ownership": AnalysisView(
        "team_ownership",
        ViewConfig(
            title="Team Ownership",
            description="Team-based resource ownership and responsibilities",
            icon="👥",
        )
    ),
    "cost_optimization": AnalysisView(
        "cost_optimization",
        ViewConfig(
            title="Cost Optimization",
            description="Cost center analysis and optimization opportunities",
            icon="💰",
        )
    ),
}
