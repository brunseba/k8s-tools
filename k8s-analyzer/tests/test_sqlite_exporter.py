"""
Tests for SQLite exporter functionality.
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from k8s_analyzer.models import ClusterState, ResourceStatus, KubernetesResource, ResourceRelationship, RelationshipType, ResourceMetadata
from k8s_analyzer.sqlite_exporter import SQLiteExporter, export_cluster_to_sqlite


class TestSQLiteExporter:
    """Test SQLite export functionality."""

    @pytest.fixture
    def sample_cluster_state(self) -> ClusterState:
        """Create sample cluster state for testing."""
        resources = [
            KubernetesResource(
                api_version="v1",
                kind="Pod",
                metadata=ResourceMetadata(
                    name="test-pod",
                    namespace="default",
                    uid="pod-123",
                    labels={"app": "test", "version": "v1"},
                    annotations={"deployment.kubernetes.io/revision": "1"}
                ),
                spec={"containers": [{"name": "app", "image": "nginx:1.20"}]},
                status={"phase": "Running"},
                health_status=ResourceStatus.HEALTHY,
                issues=[]
            ),
            KubernetesResource(
                api_version="v1",
                kind="Service",
                metadata=ResourceMetadata(
                    name="test-service",
                    namespace="default",
                    uid="svc-456",
                    labels={"app": "test"}
                ),
                spec={"selector": {"app": "test"}, "ports": [{"port": 80}]},
                health_status=ResourceStatus.WARNING,
                issues=["No endpoints found"]
            )
        ]
        
        # Create ResourceReference objects
        from k8s_analyzer.models import ResourceReference
        
        source_ref = ResourceReference(
            api_version="v1",
            kind="Service",
            name="test-service",
            namespace="default",
            uid="svc-456"
        )
        
        target_ref = ResourceReference(
            api_version="v1",
            kind="Pod",
            name="test-pod",
            namespace="default",
            uid="pod-123"
        )
        
        relationships = [
            ResourceRelationship(
                source=source_ref,
                target=target_ref,
                relationship_type=RelationshipType.SELECTS
            )
        ]
        
        cluster_state = ClusterState(
            resources=resources,
            relationships=relationships,
            cluster_info={"cluster_name": "test-cluster", "version": "1.23.0"}
        )
        cluster_state.generate_summary()
        
        return cluster_state

    def test_sqlite_exporter_context_manager(self) -> None:
        """Test SQLite exporter as context manager."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with SQLiteExporter(db_path) as exporter:
                assert exporter.connection is not None
                exporter.create_schema()
            
            # Should be closed after context
            assert exporter.connection is None
            
            # Verify database file exists and has tables
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            expected_tables = {
                "resources", "relationships", "cluster_info", 
                "analysis_summary", "resource_health_history"
            }
            assert expected_tables.issubset(set(tables))
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_export_cluster_state(self, sample_cluster_state: ClusterState) -> None:
        """Test exporting complete cluster state."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with SQLiteExporter(db_path) as exporter:
                exporter.create_schema()
                exporter.export_cluster_state(sample_cluster_state)
            
            # Verify data was exported
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check resources
            cursor.execute("SELECT * FROM resources")
            resources = cursor.fetchall()
            assert len(resources) == 2
            
            pod_resource = next(r for r in resources if r['kind'] == 'Pod')
            assert pod_resource['name'] == 'test-pod'
            assert pod_resource['namespace'] == 'default'
            assert pod_resource['health_status'] == 'healthy'
            assert json.loads(pod_resource['labels'])['app'] == 'test'
            
            service_resource = next(r for r in resources if r['kind'] == 'Service')
            assert service_resource['name'] == 'test-service'
            assert service_resource['health_status'] == 'warning'
            assert json.loads(service_resource['issues']) == ['No endpoints found']
            
            # Check relationships
            cursor.execute("SELECT * FROM relationships")
            relationships = cursor.fetchall()
            assert len(relationships) == 1
            
            rel = relationships[0]
            assert rel['source_uid'] == 'svc-456'
            assert rel['relationship_type'] == 'selects'
            assert rel['target_resource'] == 'Pod/test-pod/default'
            
            # Check cluster info
            cursor.execute("SELECT * FROM cluster_info")
            cluster_info = cursor.fetchall()
            assert len(cluster_info) == 2
            
            # Check analysis summary
            cursor.execute("SELECT * FROM analysis_summary")
            summary = cursor.fetchall()
            assert len(summary) == 1
            assert summary[0]['total_resources'] == 2
            assert summary[0]['total_relationships'] == 1
            
            conn.close()
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_query_resources(self, sample_cluster_state: ClusterState) -> None:
        """Test querying resources with filters."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with SQLiteExporter(db_path) as exporter:
                exporter.create_schema()
                exporter.export_cluster_state(sample_cluster_state)
                
                # Test query by kind
                pods = exporter.query_resources(kind="Pod")
                assert len(pods) == 1
                assert pods[0]['name'] == 'test-pod'
                
                # Test query by namespace
                default_resources = exporter.query_resources(namespace="default")
                assert len(default_resources) == 2
                
                # Test query by health status
                healthy_resources = exporter.query_resources(health_status="healthy")
                assert len(healthy_resources) == 1
                assert healthy_resources[0]['kind'] == 'Pod'
                
                warning_resources = exporter.query_resources(health_status="warning")
                assert len(warning_resources) == 1
                assert warning_resources[0]['kind'] == 'Service'
                
                # Test query resources with issues
                resources_with_issues = exporter.query_resources(has_issues=True)
                assert len(resources_with_issues) == 1
                assert resources_with_issues[0]['kind'] == 'Service'
                
                resources_without_issues = exporter.query_resources(has_issues=False)
                assert len(resources_without_issues) == 1
                assert resources_without_issues[0]['kind'] == 'Pod'
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_query_relationships(self, sample_cluster_state: ClusterState) -> None:
        """Test querying relationships with filters."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with SQLiteExporter(db_path) as exporter:
                exporter.create_schema()
                exporter.export_cluster_state(sample_cluster_state)
                
                # Test query by source kind
                service_rels = exporter.query_relationships(source_kind="Service")
                assert len(service_rels) == 1
                assert service_rels[0]['relationship_type'] == 'selects'
                
                # Test query by relationship type
                selects_rels = exporter.query_relationships(relationship_type="selects")
                assert len(selects_rels) == 1
                
                # Test query with no matches
                pod_rels = exporter.query_relationships(source_kind="Pod")
                assert len(pod_rels) == 0
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_get_health_summary(self, sample_cluster_state: ClusterState) -> None:
        """Test getting health summary statistics."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with SQLiteExporter(db_path) as exporter:
                exporter.create_schema()
                exporter.export_cluster_state(sample_cluster_state)
                
                summary = exporter.get_health_summary()
                
                assert summary['total_resources'] == 2
                assert summary['total_relationships'] == 1
                assert summary['issues_count'] == 1
                
                assert summary['health_status']['healthy'] == 1
                assert summary['health_status']['warning'] == 1
                
                assert summary['resource_type_distribution']['Pod'] == 1
                assert summary['resource_type_distribution']['Service'] == 1
                
                assert summary['namespace_distribution']['default'] == 2
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_export_to_csv(self, sample_cluster_state: ClusterState) -> None:
        """Test exporting database to CSV files."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        with tempfile.TemporaryDirectory() as csv_dir:
            try:
                with SQLiteExporter(db_path) as exporter:
                    exporter.create_schema()
                    exporter.export_cluster_state(sample_cluster_state)
                    exporter.export_to_csv(csv_dir)
                
                # Verify CSV files were created
                csv_path = Path(csv_dir)
                assert (csv_path / "resources.csv").exists()
                assert (csv_path / "relationships.csv").exists()
                
                # Check resources CSV content
                resources_csv = (csv_path / "resources.csv").read_text()
                assert "test-pod" in resources_csv
                assert "test-service" in resources_csv
                assert "healthy" in resources_csv
                assert "warning" in resources_csv
                
                # Check relationships CSV content
                relationships_csv = (csv_path / "relationships.csv").read_text()
                assert "selects" in relationships_csv
                assert "Pod/test-pod/default" in relationships_csv
                
            finally:
                Path(db_path).unlink(missing_ok=True)

    def test_replace_vs_append_mode(self, sample_cluster_state: ClusterState) -> None:
        """Test replace vs append mode for data export."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # First export
            with SQLiteExporter(db_path) as exporter:
                exporter.create_schema()
                exporter.export_cluster_state(sample_cluster_state, replace_existing=True)
            
            # Check initial count
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resources")
            initial_count = cursor.fetchone()[0]
            assert initial_count == 2
            conn.close()
            
            # Export again with replace=True (should still be 2)
            with SQLiteExporter(db_path) as exporter:
                exporter.export_cluster_state(sample_cluster_state, replace_existing=True)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resources")
            replace_count = cursor.fetchone()[0]
            assert replace_count == 2
            conn.close()
            
            # Export again with replace=False (should be 4)
            with SQLiteExporter(db_path) as exporter:
                exporter.export_cluster_state(sample_cluster_state, replace_existing=False)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resources")
            append_count = cursor.fetchone()[0]
            assert append_count == 4
            conn.close()
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_convenience_function(self, sample_cluster_state: ClusterState) -> None:
        """Test the convenience export function."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            export_cluster_to_sqlite(sample_cluster_state, db_path)
            
            # Verify data was exported
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resources")
            count = cursor.fetchone()[0]
            assert count == 2
            conn.close()
            
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_health_history_tracking(self, sample_cluster_state: ClusterState) -> None:
        """Test that health history is tracked."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        
        try:
            with SQLiteExporter(db_path) as exporter:
                exporter.create_schema()
                exporter.export_cluster_state(sample_cluster_state)
            
            # Check health history was recorded
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resource_health_history")
            history_count = cursor.fetchone()[0]
            assert history_count == 2  # One for each resource
            
            cursor.execute("SELECT resource_uid, health_status FROM resource_health_history")
            history_records = cursor.fetchall()
            
            uids_and_health = {record[0]: record[1] for record in history_records}
            assert uids_and_health['pod-123'] == 'healthy'
            assert uids_and_health['svc-456'] == 'warning'
            
            conn.close()
            
        finally:
            Path(db_path).unlink(missing_ok=True)
