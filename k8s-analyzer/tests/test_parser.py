"""
Tests for the Kubernetes resource parser.
"""

import json
from pathlib import Path

import pytest
import yaml

from k8s_analyzer.models import ClusterState, KubernetesResource
from k8s_analyzer.parser import ResourceParser


class TestResourceParser:
    """Test the ResourceParser class."""
    
    def test_parser_initialization(self) -> None:
        """Test parser initializes correctly."""
        parser = ResourceParser()
        assert parser.parsed_count == 0
        assert parser.error_count == 0
        assert parser.skipped_count == 0
    
    def test_parse_single_pod_json(self, tmp_path: Path) -> None:
        """Test parsing a single pod from JSON."""
        pod_data = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "test-pod",
                "namespace": "default",
                "labels": {"app": "test"}
            },
            "spec": {
                "containers": [{"name": "test", "image": "nginx"}]
            }
        }
        
        # Create temporary JSON file
        json_file = tmp_path / "pod.json"
        json_file.write_text(json.dumps(pod_data))
        
        # Parse the file
        parser = ResourceParser()
        cluster_state = parser.parse_file(json_file)
        
        # Verify results
        assert len(cluster_state.resources) == 1
        pod = cluster_state.resources[0]
        assert pod.kind == "Pod"
        assert pod.metadata.name == "test-pod"
        assert pod.metadata.namespace == "default"
        assert parser.parsed_count == 1
    
    def test_parse_kubectl_export_list(self, tmp_path: Path) -> None:
        """Test parsing kubectl export with List kind."""
        export_data = {
            "apiVersion": "v1",
            "kind": "List",
            "items": [
                {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": "pod1", "namespace": "default"},
                    "spec": {"containers": [{"name": "c1", "image": "nginx"}]}
                },
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": "svc1", "namespace": "default"},
                    "spec": {"selector": {"app": "test"}}
                }
            ]
        }
        
        # Create temporary JSON file
        json_file = tmp_path / "export.json"
        json_file.write_text(json.dumps(export_data))
        
        # Parse the file
        parser = ResourceParser()
        cluster_state = parser.parse_file(json_file)
        
        # Verify results
        assert len(cluster_state.resources) == 2
        assert parser.parsed_count == 2
        
        kinds = {r.kind for r in cluster_state.resources}
        assert kinds == {"Pod", "Service"}
    
    def test_parse_yaml_content(self, tmp_path: Path) -> None:
        """Test parsing YAML content."""
        yaml_content = """
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: test-config
          namespace: default
        data:
          key1: value1
          key2: value2
        """
        
        # Create temporary YAML file
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)
        
        # Parse the file
        parser = ResourceParser()
        cluster_state = parser.parse_file(yaml_file)
        
        # Verify results
        assert len(cluster_state.resources) == 1
        config_map = cluster_state.resources[0]
        assert config_map.kind == "ConfigMap"
        assert config_map.metadata.name == "test-config"
    
    def test_skip_unsupported_resources(self, tmp_path: Path) -> None:
        """Test that unsupported resource types are skipped."""
        export_data = {
            "apiVersion": "v1",
            "kind": "List",
            "items": [
                {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": "pod1", "namespace": "default"},
                    "spec": {"containers": [{"name": "c1", "image": "nginx"}]}
                },
                {
                    "apiVersion": "apps/v1",
                    "kind": "CustomResource",  # Unsupported
                    "metadata": {"name": "custom1", "namespace": "default"},
                    "spec": {}
                }
            ]
        }
        
        # Create temporary JSON file
        json_file = tmp_path / "export.json"
        json_file.write_text(json.dumps(export_data))
        
        # Parse the file
        parser = ResourceParser()
        cluster_state = parser.parse_file(json_file)
        
        # Verify results
        assert len(cluster_state.resources) == 1  # Only Pod should be parsed
        assert parser.parsed_count == 1
        assert parser.skipped_count == 1
    
    def test_parse_multiple_files(self, tmp_path: Path) -> None:
        """Test parsing multiple files."""
        # Create first file with pod
        pod_data = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "pod1", "namespace": "default"},
            "spec": {"containers": [{"name": "c1", "image": "nginx"}]}
        }
        file1 = tmp_path / "pod.json"
        file1.write_text(json.dumps(pod_data))
        
        # Create second file with service
        service_data = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "svc1", "namespace": "default"},
            "spec": {"selector": {"app": "test"}}
        }
        file2 = tmp_path / "service.json"
        file2.write_text(json.dumps(service_data))
        
        # Parse multiple files
        parser = ResourceParser()
        cluster_state = parser.parse_multiple_files([file1, file2])
        
        # Verify results
        assert len(cluster_state.resources) == 2
        assert parser.parsed_count == 2
        
        kinds = {r.kind for r in cluster_state.resources}
        assert kinds == {"Pod", "Service"}
    
    def test_get_parse_stats(self) -> None:
        """Test getting parse statistics."""
        parser = ResourceParser()
        parser.parsed_count = 5
        parser.error_count = 1
        parser.skipped_count = 2
        
        stats = parser.get_parse_stats()
        
        assert stats == {
            "parsed": 5,
            "errors": 1,
            "skipped": 2,
            "total": 8
        }


@pytest.fixture
def sample_pod_data() -> dict:
    """Sample pod data for testing."""
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "test-pod",
            "namespace": "default",
            "uid": "12345",
            "labels": {"app": "test", "version": "v1"},
            "annotations": {"deployment.kubernetes.io/revision": "1"}
        },
        "spec": {
            "containers": [
                {
                    "name": "app",
                    "image": "nginx:1.20",
                    "env": [
                        {
                            "name": "CONFIG_VALUE",
                            "valueFrom": {
                                "configMapKeyRef": {
                                    "name": "app-config",
                                    "key": "config.yaml"
                                }
                            }
                        }
                    ]
                }
            ],
            "serviceAccountName": "app-service-account",
            "nodeName": "worker-node-1"
        },
        "status": {
            "phase": "Running",
            "containerStatuses": [
                {
                    "name": "app",
                    "ready": True,
                    "restartCount": 0
                }
            ]
        }
    }


def test_parse_kubectl_export_function(sample_pod_data: dict, tmp_path: Path) -> None:
    """Test the convenience parse_kubectl_export function."""
    from k8s_analyzer.parser import parse_kubectl_export
    
    # Create export file
    export_data = {
        "apiVersion": "v1",
        "kind": "List",
        "items": [sample_pod_data]
    }
    
    json_file = tmp_path / "export.json"
    json_file.write_text(json.dumps(export_data))
    
    # Parse using convenience function
    cluster_state = parse_kubectl_export(json_file)
    
    # Verify results
    assert len(cluster_state.resources) == 1
    pod = cluster_state.resources[0]
    assert pod.kind == "Pod"
    assert pod.metadata.name == "test-pod"
    assert isinstance(cluster_state, ClusterState)
