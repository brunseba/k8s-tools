"""
Tests for the Kubernetes resource parser.
"""

import json
import os
from pathlib import Path

import pytest
import yaml

from k8s_analyzer.models import ClusterState, KubernetesResource
from k8s_analyzer.parser import ResourceParser, find_kubernetes_files, discover_and_parse


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


class TestFileDiscovery:
    """Test file discovery and batch processing capabilities."""
    
    def test_find_kubernetes_files_default_patterns(self, tmp_path: Path) -> None:
        """Test finding Kubernetes files with default patterns."""
        # Create test files
        (tmp_path / "pod.yaml").write_text("apiVersion: v1\nkind: Pod")
        (tmp_path / "service.yml").write_text("apiVersion: v1\nkind: Service")
        (tmp_path / "config.json").write_text('{"apiVersion": "v1", "kind": "ConfigMap"}')
        (tmp_path / "deployment-export.yaml").write_text("apiVersion: apps/v1\nkind: Deployment")
        (tmp_path / "kubectl-all.json").write_text('{"kind": "List", "items": []}')
        (tmp_path / "readme.txt").write_text("This is not a Kubernetes file")
        
        # Find files
        files = find_kubernetes_files(tmp_path)
        
        # Should find all Kubernetes files but not readme.txt
        assert len(files) == 5
        file_names = {f.name for f in files}
        assert "pod.yaml" in file_names
        assert "service.yml" in file_names
        assert "config.json" in file_names
        assert "deployment-export.yaml" in file_names
        assert "kubectl-all.json" in file_names
        assert "readme.txt" not in file_names
    
    def test_find_kubernetes_files_custom_patterns(self, tmp_path: Path) -> None:
        """Test finding files with custom patterns."""
        # Create test files
        (tmp_path / "my-pod.yaml").write_text("apiVersion: v1\nkind: Pod")
        (tmp_path / "my-service.yml").write_text("apiVersion: v1\nkind: Service")
        (tmp_path / "other.yaml").write_text("apiVersion: v1\nkind: ConfigMap")
        
        # Find files with custom pattern
        files = find_kubernetes_files(tmp_path, patterns=["my-*.yaml", "my-*.yml"])
        
        # Should only find files matching "my-*" pattern
        assert len(files) == 2
        file_names = {f.name for f in files}
        assert "my-pod.yaml" in file_names
        assert "my-service.yml" in file_names
        assert "other.yaml" not in file_names
    
    def test_find_kubernetes_files_recursive(self, tmp_path: Path) -> None:
        """Test recursive file discovery."""
        # Create nested directory structure
        subdir = tmp_path / "manifests" / "apps"
        subdir.mkdir(parents=True)
        
        # Create files in different directories
        (tmp_path / "namespace.yaml").write_text("apiVersion: v1\nkind: Namespace")
        (tmp_path / "manifests" / "service.yaml").write_text("apiVersion: v1\nkind: Service")
        (subdir / "deployment.yaml").write_text("apiVersion: apps/v1\nkind: Deployment")
        
        # Test recursive search (default)
        files = find_kubernetes_files(tmp_path, recursive=True)
        assert len(files) == 3
        
        # Test non-recursive search
        files_non_recursive = find_kubernetes_files(tmp_path, recursive=False)
        assert len(files_non_recursive) == 1
        assert files_non_recursive[0].name == "namespace.yaml"
    
    def test_find_kubernetes_files_single_file(self, tmp_path: Path) -> None:
        """Test finding a single file instead of directory."""
        # Create a single file
        single_file = tmp_path / "pod.yaml"
        single_file.write_text("apiVersion: v1\nkind: Pod")
        
        # Find files using the file path directly
        files = find_kubernetes_files(single_file)
        
        assert len(files) == 1
        assert files[0] == single_file
    
    def test_discover_and_parse(self, tmp_path: Path) -> None:
        """Test discovering and parsing all files in a directory."""
        # Create test files with valid Kubernetes resources
        pod_data = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "test-pod", "namespace": "default"},
            "spec": {"containers": [{"name": "c1", "image": "nginx"}]}
        }
        
        service_data = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "test-service", "namespace": "default"},
            "spec": {"selector": {"app": "test"}}
        }
        
        # Create files
        (tmp_path / "pod.json").write_text(json.dumps(pod_data))
        (tmp_path / "service.yaml").write_text(yaml.dump(service_data))
        
        # Discover and parse
        cluster_state = discover_and_parse(tmp_path)
        
        # Verify results
        assert len(cluster_state.resources) == 2
        kinds = {r.kind for r in cluster_state.resources}
        assert kinds == {"Pod", "Service"}
    
    def test_discover_and_parse_with_max_files(self, tmp_path: Path) -> None:
        """Test discover and parse with file limit."""
        # Create multiple test files
        for i in range(5):
            pod_data = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": f"pod-{i}", "namespace": "default"},
                "spec": {"containers": [{"name": "c1", "image": "nginx"}]}
            }
            (tmp_path / f"pod-{i}.json").write_text(json.dumps(pod_data))
        
        # Discover and parse with limit
        cluster_state = discover_and_parse(tmp_path, max_files=3)
        
        # Should only process 3 files
        assert len(cluster_state.resources) == 3
    
    def test_discover_and_parse_empty_directory(self, tmp_path: Path) -> None:
        """Test discover and parse with no matching files."""
        # Create non-Kubernetes files
        (tmp_path / "readme.txt").write_text("Not a Kubernetes file")
        (tmp_path / "config.ini").write_text("[section]\nkey=value")
        
        # Discover and parse
        cluster_state = discover_and_parse(tmp_path)
        
        # Should return empty cluster state
        assert len(cluster_state.resources) == 0
    
    def test_find_kubernetes_files_nonexistent_path(self) -> None:
        """Test finding files in nonexistent path."""
        with pytest.raises(FileNotFoundError):
            find_kubernetes_files("/nonexistent/path")
