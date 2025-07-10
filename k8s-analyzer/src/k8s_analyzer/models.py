"""
Kubernetes resource data models and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    """Types of relationships between Kubernetes resources."""
    
    OWNS = "owns"
    USES = "uses"
    EXPOSES = "exposes"
    BINDS = "binds"
    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    MANAGES = "manages"
    SELECTS = "selects"


class RelationshipDirection(str, Enum):
    """Direction of relationships."""
    
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    BIDIRECTIONAL = "bidirectional"


class ResourceStatus(str, Enum):
    """Resource health status."""
    
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class ResourceMetadata(BaseModel):
    """Kubernetes resource metadata model."""
    
    name: str
    namespace: Optional[str] = None
    uid: Optional[str] = None
    resource_version: Optional[str] = None
    generation: Optional[int] = None
    creation_timestamp: Optional[datetime] = None
    deletion_timestamp: Optional[datetime] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    owner_references: List[Dict[str, Any]] = Field(default_factory=list)
    finalizers: List[str] = Field(default_factory=list)


class ResourceReference(BaseModel):
    """Reference to a Kubernetes resource."""
    
    api_version: str
    kind: str
    name: str
    namespace: Optional[str] = None
    uid: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the resource reference."""
        if self.namespace:
            return f"{self.kind}/{self.name}/{self.namespace}"
        return f"{self.kind}/{self.name}"
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash((self.api_version, self.kind, self.name, self.namespace))


class ResourceRelationship(BaseModel):
    """Relationship between two Kubernetes resources."""
    
    source: ResourceReference
    target: ResourceReference
    relationship_type: RelationshipType
    direction: RelationshipDirection = RelationshipDirection.OUTBOUND
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the relationship."""
        return f"{self.source} {self.relationship_type.value} {self.target}"


class KubernetesResource(BaseModel):
    """Base Kubernetes resource model."""
    
    api_version: str
    kind: str
    metadata: ResourceMetadata
    spec: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[Dict[str, Any]] = None
    relationships: List[ResourceRelationship] = Field(default_factory=list)
    health_status: ResourceStatus = ResourceStatus.UNKNOWN
    issues: List[str] = Field(default_factory=list)
    
    @property
    def ref(self) -> ResourceReference:
        """Get resource reference."""
        return ResourceReference(
            api_version=self.api_version,
            kind=self.kind,
            name=self.metadata.name,
            namespace=self.metadata.namespace,
            uid=self.metadata.uid,
        )
    
    @property
    def full_name(self) -> str:
        """Get full resource name with namespace."""
        if self.metadata.namespace:
            return f"{self.kind}/{self.metadata.name}/{self.metadata.namespace}"
        return f"{self.kind}/{self.metadata.name}"
    
    def add_relationship(
        self,
        target: "KubernetesResource",
        relationship_type: RelationshipType,
        direction: RelationshipDirection = RelationshipDirection.OUTBOUND,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a relationship to another resource."""
        relationship = ResourceRelationship(
            source=self.ref,
            target=target.ref,
            relationship_type=relationship_type,
            direction=direction,
            metadata=metadata or {},
        )
        self.relationships.append(relationship)
    
    def get_relationships_by_type(
        self, relationship_type: RelationshipType
    ) -> List[ResourceRelationship]:
        """Get relationships of a specific type."""
        return [
            rel for rel in self.relationships 
            if rel.relationship_type == relationship_type
        ]


class ClusterState(BaseModel):
    """Complete state of analyzed Kubernetes cluster resources."""
    
    resources: List[KubernetesResource] = Field(default_factory=list)
    relationships: List[ResourceRelationship] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    cluster_info: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    
    def add_resource(self, resource: KubernetesResource) -> None:
        """Add a resource to the cluster state."""
        self.resources.append(resource)
    
    def get_resources_by_kind(self, kind: str) -> List[KubernetesResource]:
        """Get all resources of a specific kind."""
        return [res for res in self.resources if res.kind == kind]
    
    def get_resource_by_ref(self, ref: ResourceReference) -> Optional[KubernetesResource]:
        """Get a resource by its reference."""
        for resource in self.resources:
            if resource.ref == ref:
                return resource
        return None
    
    def get_namespaces(self) -> Set[str]:
        """Get all unique namespaces in the cluster."""
        namespaces = set()
        for resource in self.resources:
            if resource.metadata.namespace:
                namespaces.add(resource.metadata.namespace)
        return namespaces
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate cluster analysis summary."""
        resource_counts = {}
        namespace_counts = {}
        status_counts = {status.value: 0 for status in ResourceStatus}
        
        for resource in self.resources:
            # Count by kind
            resource_counts[resource.kind] = resource_counts.get(resource.kind, 0) + 1
            
            # Count by namespace
            ns = resource.metadata.namespace or "cluster-scoped"
            namespace_counts[ns] = namespace_counts.get(ns, 0) + 1
            
            # Count by status
            status_counts[resource.health_status.value] += 1
        
        self.summary = {
            "total_resources": len(self.resources),
            "total_relationships": len(self.relationships),
            "resource_types": resource_counts,
            "namespaces": namespace_counts,
            "health_status": status_counts,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
        }
        
        return self.summary


# Specific resource type models for better type safety
class Pod(KubernetesResource):
    """Pod-specific resource model."""
    
    @property
    def containers(self) -> List[Dict[str, Any]]:
        """Get pod containers."""
        return self.spec.get("containers", [])
    
    @property
    def service_account(self) -> Optional[str]:
        """Get pod service account."""
        return self.spec.get("serviceAccountName", "default")
    
    @property
    def node_name(self) -> Optional[str]:
        """Get node where pod is scheduled."""
        return self.spec.get("nodeName")


class Service(KubernetesResource):
    """Service-specific resource model."""
    
    @property
    def selector(self) -> Dict[str, str]:
        """Get service selector."""
        return self.spec.get("selector", {})
    
    @property
    def ports(self) -> List[Dict[str, Any]]:
        """Get service ports."""
        return self.spec.get("ports", [])


class ConfigMap(KubernetesResource):
    """ConfigMap-specific resource model."""
    
    @property
    def data(self) -> Dict[str, str]:
        """Get ConfigMap data."""
        return self.spec.get("data", {})


class PersistentVolumeClaim(KubernetesResource):
    """PVC-specific resource model."""
    
    @property
    def storage_class(self) -> Optional[str]:
        """Get storage class name."""
        return self.spec.get("storageClassName")
    
    @property
    def access_modes(self) -> List[str]:
        """Get access modes."""
        return self.spec.get("accessModes", [])


class Node(KubernetesResource):
    """Node-specific resource model."""
    
    @property
    def addresses(self) -> List[Dict[str, str]]:
        """Get node addresses."""
        return self.status.get("addresses", []) if self.status else []
    
    @property
    def conditions(self) -> List[Dict[str, Any]]:
        """Get node conditions."""
        return self.status.get("conditions", []) if self.status else []
