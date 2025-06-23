"""
Kubernetes resource parser for JSON/YAML exports.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import glob
import os

import yaml
from pydantic import ValidationError

from .models import (
    ClusterState,
    ConfigMap,
    KubernetesResource,
    Node,
    PersistentVolumeClaim,
    Pod,
    ResourceMetadata,
    Service,
)

logger = logging.getLogger(__name__)


class ResourceParser:
    """Parser for Kubernetes resource exports."""
    
    SUPPORTED_KINDS = {
        "Pod",
        "Service", 
        "ConfigMap",
        "Node",
        "Namespace",
        "PersistentVolume",
        "PersistentVolumeClaim",
        "RoleBinding",
        "Ingress",
        "ServiceAccount",
    }
    
    def __init__(self) -> None:
        """Initialize the resource parser."""
        self.parsed_count = 0
        self.error_count = 0
        self.skipped_count = 0
    
    def parse_file(self, file_path: Union[str, Path]) -> ClusterState:
        """Parse a kubectl export file and return cluster state."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Parsing file: {file_path}")
        
        # Determine file format
        content = file_path.read_text(encoding="utf-8")
        
        if file_path.suffix.lower() in {".json"}:
            return self._parse_json_content(content)
        elif file_path.suffix.lower() in {".yaml", ".yml"}:
            return self._parse_yaml_content(content)
        else:
            # Try to detect format from content
            try:
                return self._parse_json_content(content)
            except json.JSONDecodeError:
                return self._parse_yaml_content(content)
    
    def parse_multiple_files(self, file_paths: List[Union[str, Path]]) -> ClusterState:
        """Parse multiple export files and merge into single cluster state."""
        cluster_state = ClusterState()
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                logger.info(f"Processing file {i}/{total_files}: {Path(file_path).name}")
                file_cluster_state = self.parse_file(file_path)
                
                # Merge resources
                cluster_state.resources.extend(file_cluster_state.resources)
                cluster_state.relationships.extend(file_cluster_state.relationships)
                
                # Merge cluster info
                cluster_state.cluster_info.update(file_cluster_state.cluster_info)
                
                # Log progress every 10 files or on completion
                if i % 10 == 0 or i == total_files:
                    logger.info(f"Progress: {i}/{total_files} files processed")
                
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {e}")
                self.error_count += 1
        
        cluster_state.generate_summary()
        return cluster_state
    
    def _parse_json_content(self, content: str) -> ClusterState:
        """Parse JSON content."""
        try:
            data = json.loads(content)
            return self._parse_kubectl_export(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON content: {e}")
            raise
    
    def _parse_yaml_content(self, content: str) -> ClusterState:
        """Parse YAML content."""
        try:
            # Handle multi-document YAML
            documents = list(yaml.safe_load_all(content))
            
            if len(documents) == 1 and isinstance(documents[0], dict):
                # Single document - might be kubectl export
                return self._parse_kubectl_export(documents[0])
            else:
                # Multiple documents - parse each as individual resource
                return self._parse_multiple_resources(documents)
                
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML content: {e}")
            raise
    
    def _parse_kubectl_export(self, data: Dict[str, Any]) -> ClusterState:
        """Parse kubectl get all -o json/yaml export format."""
        cluster_state = ClusterState()
        
        # Check if this is a List type (kubectl export format)
        if data.get("kind") == "List" and "items" in data:
            items = data["items"]
            logger.info(f"Found {len(items)} items in kubectl export")
            
            for item in items:
                resource = self._parse_single_resource(item)
                if resource:
                    cluster_state.add_resource(resource)
        else:
            # Single resource
            resource = self._parse_single_resource(data)
            if resource:
                cluster_state.add_resource(resource)
        
        cluster_state.generate_summary()
        return cluster_state
    
    def _parse_multiple_resources(self, documents: List[Dict[str, Any]]) -> ClusterState:
        """Parse multiple individual resources."""
        cluster_state = ClusterState()
        
        for doc in documents:
            if doc is None:
                continue
                
            resource = self._parse_single_resource(doc)
            if resource:
                cluster_state.add_resource(resource)
        
        cluster_state.generate_summary()
        return cluster_state
    
    def _parse_single_resource(self, data: Dict[str, Any]) -> Optional[KubernetesResource]:
        """Parse a single Kubernetes resource."""
        try:
            kind = data.get("kind")
            
            if not kind:
                logger.warning("Resource missing 'kind' field, skipping")
                self.skipped_count += 1
                return None
            
            if kind not in self.SUPPORTED_KINDS:
                logger.debug(f"Unsupported resource kind: {kind}, skipping")
                self.skipped_count += 1
                return None
            
            # Parse metadata
            metadata_data = data.get("metadata", {})
            metadata = self._parse_metadata(metadata_data)
            
            # Create appropriate resource type
            resource_class = self._get_resource_class(kind)
            
            resource = resource_class(
                api_version=data.get("apiVersion", "v1"),
                kind=kind,
                metadata=metadata,
                spec=data.get("spec", {}),
                status=data.get("status"),
            )
            
            self.parsed_count += 1
            logger.debug(f"Parsed {kind}: {metadata.name}")
            return resource
            
        except ValidationError as e:
            logger.error(f"Validation error parsing resource: {e}")
            self.error_count += 1
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing resource: {e}")
            self.error_count += 1
            return None
    
    def _parse_metadata(self, metadata_data: Dict[str, Any]) -> ResourceMetadata:
        """Parse resource metadata."""
        # Parse timestamps
        creation_timestamp = None
        deletion_timestamp = None
        
        if "creationTimestamp" in metadata_data:
            creation_timestamp = self._parse_timestamp(metadata_data["creationTimestamp"])
        
        if "deletionTimestamp" in metadata_data:
            deletion_timestamp = self._parse_timestamp(metadata_data["deletionTimestamp"])
        
        return ResourceMetadata(
            name=metadata_data.get("name", ""),
            namespace=metadata_data.get("namespace"),
            uid=metadata_data.get("uid"),
            resource_version=metadata_data.get("resourceVersion"),
            generation=metadata_data.get("generation"),
            creation_timestamp=creation_timestamp,
            deletion_timestamp=deletion_timestamp,
            labels=metadata_data.get("labels", {}),
            annotations=metadata_data.get("annotations", {}),
            owner_references=metadata_data.get("ownerReferences", []),
            finalizers=metadata_data.get("finalizers", []),
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse Kubernetes timestamp string."""
        try:
            # Kubernetes uses RFC3339 format
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse timestamp: {timestamp_str}")
            return None
    
    def _get_resource_class(self, kind: str) -> type:
        """Get the appropriate resource class for a kind."""
        class_mapping = {
            "Pod": Pod,
            "Service": Service,
            "ConfigMap": ConfigMap,
            "Node": Node,
            "PersistentVolumeClaim": PersistentVolumeClaim,
        }
        
        return class_mapping.get(kind, KubernetesResource)
    
    def get_parse_stats(self) -> Dict[str, int]:
        """Get parsing statistics."""
        return {
            "parsed": self.parsed_count,
            "errors": self.error_count,
            "skipped": self.skipped_count,
            "total": self.parsed_count + self.error_count + self.skipped_count,
        }


def find_kubernetes_files(
    path: Union[str, Path],
    patterns: Optional[List[str]] = None,
    recursive: bool = True
) -> List[Path]:
    """
    Find Kubernetes files in a directory using glob patterns.
    
    Args:
        path: Directory path to search
        patterns: Glob patterns to match (default: kubernetes-related patterns)
        recursive: Whether to search recursively
    
    Returns:
        List of matching file paths
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    if not path.is_dir():
        # If it's a file, return it if it matches patterns
        if not patterns or any(path.match(pattern) for pattern in patterns):
            return [path]
        return []
    
    # Default patterns for Kubernetes files
    if not patterns:
        patterns = [
            "*.yaml",
            "*.yml", 
            "*.json",
            "*-export.yaml",
            "*-export.yml",
            "*-export.json",
            "kubectl-*.yaml",
            "kubectl-*.yml",
            "kubectl-*.json",
        ]
    
    found_files = []
    
    for pattern in patterns:
        if recursive:
            # Use ** for recursive search
            search_pattern = path / "**" / pattern
            found_files.extend(path.glob(f"**/{pattern}"))
        else:
            # Search only in the current directory
            found_files.extend(path.glob(pattern))
    
    # Remove duplicates and sort
    unique_files = list(set(found_files))
    unique_files.sort()
    
    logger.info(f"Found {len(unique_files)} Kubernetes files in {path}")
    return unique_files


def discover_and_parse(
    path: Union[str, Path],
    patterns: Optional[List[str]] = None,
    recursive: bool = True,
    max_files: Optional[int] = None
) -> ClusterState:
    """
    Discover and parse all Kubernetes files in a directory.
    
    Args:
        path: Directory path to search
        patterns: Glob patterns to match files
        recursive: Whether to search recursively
        max_files: Maximum number of files to process
    
    Returns:
        ClusterState with parsed resources from all found files
    """
    files = find_kubernetes_files(path, patterns, recursive)
    
    if not files:
        logger.warning(f"No Kubernetes files found in {path}")
        return ClusterState()
    
    if max_files and len(files) > max_files:
        logger.warning(f"Found {len(files)} files, limiting to {max_files}")
        files = files[:max_files]
    
    logger.info(f"Parsing {len(files)} files from {path}")
    
    parser = ResourceParser()
    cluster_state = parser.parse_multiple_files(files)
    
    stats = parser.get_parse_stats()
    logger.info(f"Directory parsing complete: {stats}")
    
    return cluster_state


def parse_kubectl_export(
    file_path: Union[str, Path], 
    additional_files: Optional[List[Union[str, Path]]] = None
) -> ClusterState:
    """
    Convenience function to parse kubectl exports.
    
    Args:
        file_path: Path to the main export file
        additional_files: Optional list of additional export files to merge
    
    Returns:
        ClusterState with parsed resources
    """
    parser = ResourceParser()
    
    if additional_files:
        all_files = [file_path] + additional_files
        cluster_state = parser.parse_multiple_files(all_files)
    else:
        cluster_state = parser.parse_file(file_path)
    
    stats = parser.get_parse_stats()
    logger.info(f"Parsing complete: {stats}")
    
    return cluster_state
