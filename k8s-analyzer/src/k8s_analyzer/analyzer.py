"""
Kubernetes resource relationship analyzer.
"""

import logging
from typing import Dict, List, Optional, Set

from .models import (
    ClusterState,
    KubernetesResource,
    Pod,
    RelationshipDirection,
    RelationshipType,
    ResourceReference,
    ResourceStatus,
    Service,
)

logger = logging.getLogger(__name__)


class ResourceAnalyzer:
    """Analyzer for building relationships between Kubernetes resources."""
    
    def __init__(self) -> None:
        """Initialize the resource analyzer."""
        self.relationship_count = 0
    
    def analyze_cluster(self, cluster_state: ClusterState) -> ClusterState:
        """
        Analyze cluster resources and build relationships.
        
        Args:
            cluster_state: Parsed cluster state
            
        Returns:
            Updated cluster state with relationships and health analysis
        """
        logger.info(f"Analyzing {len(cluster_state.resources)} resources")
        
        # Build resource index for fast lookups
        resource_index = self._build_resource_index(cluster_state.resources)
        
        # Analyze relationships
        self._analyze_ownership_relationships(cluster_state.resources)
        self._analyze_service_relationships(cluster_state.resources, resource_index)
        self._analyze_pod_relationships(cluster_state.resources, resource_index)
        self._analyze_storage_relationships(cluster_state.resources, resource_index)
        self._analyze_rbac_relationships(cluster_state.resources, resource_index)
        
        # Collect all relationships
        self._collect_cluster_relationships(cluster_state)
        
        # Analyze resource health
        self._analyze_resource_health(cluster_state.resources)
        
        # Update summary
        cluster_state.generate_summary()
        
        logger.info(f"Analysis complete: {self.relationship_count} relationships found")
        return cluster_state
    
    def _build_resource_index(
        self, resources: List[KubernetesResource]
    ) -> Dict[str, KubernetesResource]:
        """Build index for fast resource lookups by full name."""
        index = {}
        for resource in resources:
            index[resource.full_name] = resource
            # Also index by name only for cluster-scoped resources
            if not resource.metadata.namespace:
                index[f"{resource.kind}/{resource.metadata.name}"] = resource
        return index
    
    def _analyze_ownership_relationships(
        self, resources: List[KubernetesResource]
    ) -> None:
        """Analyze ownership relationships from ownerReferences."""
        for resource in resources:
            for owner_ref in resource.metadata.owner_references:
                owner_kind = owner_ref.get("kind")
                owner_name = owner_ref.get("name")
                
                if not owner_kind or not owner_name:
                    continue
                
                # Find owner resource
                owner_full_name = f"{owner_kind}/{resource.metadata.namespace}/{owner_name}"
                if not resource.metadata.namespace:
                    owner_full_name = f"{owner_kind}/{owner_name}"
                
                # Create ownership relationship
                owner_ref_obj = ResourceReference(
                    api_version=owner_ref.get("apiVersion", "v1"),
                    kind=owner_kind,
                    name=owner_name,
                    namespace=resource.metadata.namespace,
                    uid=owner_ref.get("uid"),
                )
                
                resource.add_relationship(
                    target=type(resource)(
                        api_version=owner_ref.get("apiVersion", "v1"),
                        kind=owner_kind,
                        metadata=type(resource.metadata)(name=owner_name, namespace=resource.metadata.namespace),
                    ),
                    relationship_type=RelationshipType.DEPENDS_ON,
                    direction=RelationshipDirection.OUTBOUND,
                    metadata={"owner_reference": True},
                )
                
                self.relationship_count += 1
    
    def _analyze_service_relationships(
        self,
        resources: List[KubernetesResource],
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze service to pod relationships through selectors."""
        services = [r for r in resources if isinstance(r, Service)]
        pods = [r for r in resources if isinstance(r, Pod)]
        
        for service in services:
            selector = service.selector
            if not selector:
                continue
            
            # Find pods that match the selector
            for pod in pods:
                if (pod.metadata.namespace == service.metadata.namespace and 
                    self._labels_match_selector(pod.metadata.labels, selector)):
                    
                    service.add_relationship(
                        target=pod,
                        relationship_type=RelationshipType.SELECTS,
                        direction=RelationshipDirection.OUTBOUND,
                        metadata={"selector": selector},
                    )
                    
                    pod.add_relationship(
                        target=service,
                        relationship_type=RelationshipType.EXPOSES,
                        direction=RelationshipDirection.INBOUND,
                    )
                    
                    self.relationship_count += 2
    
    def _analyze_pod_relationships(
        self,
        resources: List[KubernetesResource],
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze pod relationships to other resources."""
        pods = [r for r in resources if isinstance(r, Pod)]
        
        for pod in pods:
            # Analyze ConfigMap and Secret references
            self._analyze_pod_config_relationships(pod, resource_index)
            
            # Analyze PVC relationships
            self._analyze_pod_storage_relationships(pod, resource_index)
            
            # Analyze ServiceAccount relationships
            self._analyze_pod_serviceaccount_relationships(pod, resource_index)
            
            # Analyze Node relationships
            self._analyze_pod_node_relationships(pod, resource_index)
    
    def _analyze_pod_config_relationships(
        self,
        pod: Pod,
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze pod relationships to ConfigMaps and Secrets."""
        # Check environment variables
        for container in pod.containers:
            env_vars = container.get("env", [])
            for env_var in env_vars:
                value_from = env_var.get("valueFrom", {})
                
                # ConfigMap reference
                config_map_ref = value_from.get("configMapKeyRef", {})
                if config_map_ref:
                    self._add_config_relationship(
                        pod, config_map_ref.get("name"), "ConfigMap", resource_index
                    )
                
                # Secret reference
                secret_ref = value_from.get("secretKeyRef", {})
                if secret_ref:
                    self._add_config_relationship(
                        pod, secret_ref.get("name"), "Secret", resource_index
                    )
            
            # Check volume mounts
            volume_mounts = container.get("volumeMounts", [])
            for volume_mount in volume_mounts:
                volume_name = volume_mount.get("name")
                if volume_name:
                    # Find corresponding volume in pod spec
                    volumes = pod.spec.get("volumes", [])
                    for volume in volumes:
                        if volume.get("name") == volume_name:
                            # Check for ConfigMap volume
                            if "configMap" in volume:
                                config_map_name = volume["configMap"].get("name")
                                self._add_config_relationship(
                                    pod, config_map_name, "ConfigMap", resource_index
                                )
                            
                            # Check for Secret volume
                            if "secret" in volume:
                                secret_name = volume["secret"].get("secretName")
                                self._add_config_relationship(
                                    pod, secret_name, "Secret", resource_index
                                )
    
    def _analyze_pod_storage_relationships(
        self,
        pod: Pod,
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze pod relationships to PVCs."""
        volumes = pod.spec.get("volumes", [])
        for volume in volumes:
            pvc_claim = volume.get("persistentVolumeClaim", {})
            if pvc_claim:
                claim_name = pvc_claim.get("claimName")
                if claim_name:
                    pvc_full_name = f"PersistentVolumeClaim/{pod.metadata.namespace}/{claim_name}"
                    pvc = resource_index.get(pvc_full_name)
                    
                    if pvc:
                        pod.add_relationship(
                            target=pvc,
                            relationship_type=RelationshipType.USES,
                            direction=RelationshipDirection.OUTBOUND,
                            metadata={"volume_name": volume.get("name")},
                        )
                        self.relationship_count += 1
    
    def _analyze_pod_serviceaccount_relationships(
        self,
        pod: Pod,
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze pod relationships to ServiceAccounts."""
        service_account = pod.service_account
        if service_account and service_account != "default":
            sa_full_name = f"ServiceAccount/{pod.metadata.namespace}/{service_account}"
            sa = resource_index.get(sa_full_name)
            
            if sa:
                pod.add_relationship(
                    target=sa,
                    relationship_type=RelationshipType.USES,
                    direction=RelationshipDirection.OUTBOUND,
                )
                self.relationship_count += 1
    
    def _analyze_pod_node_relationships(
        self,
        pod: Pod,
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze pod relationships to Nodes."""
        node_name = pod.node_name
        if node_name:
            node_full_name = f"Node/{node_name}"
            node = resource_index.get(node_full_name)
            
            if node:
                pod.add_relationship(
                    target=node,
                    relationship_type=RelationshipType.DEPENDS_ON,
                    direction=RelationshipDirection.OUTBOUND,
                    metadata={"scheduled": True},
                )
                self.relationship_count += 1
    
    def _analyze_storage_relationships(
        self,
        resources: List[KubernetesResource],
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze storage relationships between PVCs and PVs."""
        pvcs = [r for r in resources if r.kind == "PersistentVolumeClaim"]
        pvs = [r for r in resources if r.kind == "PersistentVolume"]
        
        for pvc in pvcs:
            # Check if PVC is bound to a PV
            if pvc.status and "volumeName" in pvc.status:
                volume_name = pvc.status["volumeName"]
                pv_full_name = f"PersistentVolume/{volume_name}"
                pv = resource_index.get(pv_full_name)
                
                if pv:
                    pvc.add_relationship(
                        target=pv,
                        relationship_type=RelationshipType.BINDS,
                        direction=RelationshipDirection.OUTBOUND,
                    )
                    self.relationship_count += 1
    
    def _analyze_rbac_relationships(
        self,
        resources: List[KubernetesResource],
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Analyze RBAC relationships."""
        role_bindings = [r for r in resources if r.kind == "RoleBinding"]
        
        for rb in role_bindings:
            subjects = rb.spec.get("subjects", [])
            role_ref = rb.spec.get("roleRef", {})
            
            # Analyze subject relationships
            for subject in subjects:
                if subject.get("kind") == "ServiceAccount":
                    sa_name = subject.get("name")
                    sa_namespace = subject.get("namespace", rb.metadata.namespace)
                    sa_full_name = f"ServiceAccount/{sa_namespace}/{sa_name}"
                    sa = resource_index.get(sa_full_name)
                    
                    if sa:
                        rb.add_relationship(
                            target=sa,
                            relationship_type=RelationshipType.REFERENCES,
                            direction=RelationshipDirection.OUTBOUND,
                            metadata={"subject": True},
                        )
                        self.relationship_count += 1
    
    def _analyze_resource_health(self, resources: List[KubernetesResource]) -> None:
        """Analyze resource health status."""
        for resource in resources:
            resource.health_status = self._assess_resource_health(resource)
    
    def _assess_resource_health(self, resource: KubernetesResource) -> ResourceStatus:
        """Assess individual resource health."""
        # Check if resource is being deleted
        if resource.metadata.deletion_timestamp:
            resource.issues.append("Resource is being deleted")
            return ResourceStatus.WARNING
        
        # Pod-specific health checks
        if isinstance(resource, Pod):
            return self._assess_pod_health(resource)
        
        # Service-specific health checks
        elif isinstance(resource, Service):
            return self._assess_service_health(resource)
        
        # Default health assessment
        if resource.status:
            # Check for common error conditions
            conditions = resource.status.get("conditions", [])
            for condition in conditions:
                if condition.get("status") == "False" and condition.get("type") in {
                    "Ready", "Available", "Progressing"
                }:
                    resource.issues.append(f"Condition {condition.get('type')} is False")
                    return ResourceStatus.ERROR
        
        return ResourceStatus.HEALTHY
    
    def _assess_pod_health(self, pod: Pod) -> ResourceStatus:
        """Assess pod-specific health."""
        if not pod.status:
            return ResourceStatus.UNKNOWN
        
        phase = pod.status.get("phase")
        
        if phase == "Failed":
            pod.issues.append("Pod is in Failed phase")
            return ResourceStatus.ERROR
        
        if phase == "Pending":
            pod.issues.append("Pod is in Pending phase")
            return ResourceStatus.WARNING
        
        if phase == "Running":
            # Check container statuses
            container_statuses = pod.status.get("containerStatuses", [])
            for status in container_statuses:
                if not status.get("ready", False):
                    pod.issues.append(f"Container {status.get('name')} is not ready")
                    return ResourceStatus.WARNING
                
                if status.get("restartCount", 0) > 5:
                    pod.issues.append(f"Container {status.get('name')} has high restart count")
                    return ResourceStatus.WARNING
        
        return ResourceStatus.HEALTHY
    
    def _assess_service_health(self, service: Service) -> ResourceStatus:
        """Assess service-specific health."""
        # Check if service has endpoints
        if service.status and "loadBalancer" in service.status:
            lb_status = service.status["loadBalancer"]
            if not lb_status.get("ingress"):
                service.issues.append("LoadBalancer service has no ingress")
                return ResourceStatus.WARNING
        
        # Check if service has valid selector
        if not service.selector:
            service.issues.append("Service has no selector")
            return ResourceStatus.WARNING
        
        return ResourceStatus.HEALTHY
    
    def _add_config_relationship(
        self,
        pod: Pod,
        config_name: Optional[str],
        config_kind: str,
        resource_index: Dict[str, KubernetesResource],
    ) -> None:
        """Add relationship from pod to ConfigMap or Secret."""
        if not config_name:
            return
        
        config_full_name = f"{config_kind}/{pod.metadata.namespace}/{config_name}"
        config_resource = resource_index.get(config_full_name)
        
        if config_resource:
            pod.add_relationship(
                target=config_resource,
                relationship_type=RelationshipType.USES,
                direction=RelationshipDirection.OUTBOUND,
            )
            self.relationship_count += 1
    
    def _labels_match_selector(
        self, labels: Dict[str, str], selector: Dict[str, str]
    ) -> bool:
        """Check if labels match a selector."""
        for key, value in selector.items():
            if labels.get(key) != value:
                return False
        return True
    
    def _collect_cluster_relationships(self, cluster_state: ClusterState) -> None:
        """Collect all relationships from resources into cluster state."""
        all_relationships = []
        for resource in cluster_state.resources:
            all_relationships.extend(resource.relationships)
        
        cluster_state.relationships = all_relationships
