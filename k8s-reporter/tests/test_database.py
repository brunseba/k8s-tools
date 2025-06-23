"""
Tests for k8s-reporter database functionality.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path

from k8s_reporter.database import DatabaseClient
from k8s_reporter.models import ResourceSummary


def create_test_database():
    """Create a test SQLite database with sample data."""
    # Create temporary database
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = db_file.name
    db_file.close()
    
    # Create database schema and sample data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables (simplified schema)
    cursor.execute("""
        CREATE TABLE resources (
            id INTEGER PRIMARY KEY,
            uid TEXT,
            name TEXT,
            namespace TEXT,
            kind TEXT,
            health_status TEXT,
            issues TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE relationships (
            id INTEGER PRIMARY KEY,
            source_uid TEXT,
            target_resource TEXT,
            relationship_type TEXT,
            source_kind TEXT,
            target_kind TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE analysis_summary (
            id INTEGER PRIMARY KEY,
            analysis_timestamp TEXT,
            total_resources INTEGER,
            total_relationships INTEGER
        )
    """)
    
    # Insert sample data
    cursor.execute("""
        INSERT INTO resources (uid, name, namespace, kind, health_status, issues)
        VALUES 
            ('pod-1', 'test-pod', 'default', 'Pod', 'healthy', '[]'),
            ('svc-1', 'test-service', 'default', 'Service', 'warning', '["No endpoints"]'),
            ('cm-1', 'config-map', 'default', 'ConfigMap', 'healthy', '[]')
    """)
    
    cursor.execute("""
        INSERT INTO relationships (source_uid, target_resource, relationship_type, source_kind, target_kind)
        VALUES ('svc-1', 'Pod/test-pod', 'selects', 'Service', 'Pod')
    """)
    
    cursor.execute("""
        INSERT INTO analysis_summary (analysis_timestamp, total_resources, total_relationships)
        VALUES ('2023-01-01T00:00:00', 3, 1)
    """)
    
    conn.commit()
    conn.close()
    
    return db_path


class TestDatabaseClient:
    """Test DatabaseClient functionality."""
    
    def test_database_client_initialization(self):
        """Test DatabaseClient initialization."""
        db_path = create_test_database()
        
        try:
            client = DatabaseClient(db_path)
            assert client.db_path.exists()
        finally:
            Path(db_path).unlink()
    
    def test_database_client_nonexistent_file(self):
        """Test DatabaseClient with nonexistent file."""
        with pytest.raises(FileNotFoundError):
            DatabaseClient("/nonexistent/path.db")
    
    def test_get_resource_summary(self):
        """Test getting resource summary."""
        db_path = create_test_database()
        
        try:
            client = DatabaseClient(db_path)
            summary = client.get_resource_summary()
            
            assert isinstance(summary, ResourceSummary)
            assert summary.total_resources == 3
            assert summary.total_relationships == 1
            assert 'healthy' in summary.health_distribution
            assert 'warning' in summary.health_distribution
            assert 'Pod' in summary.resource_types
            assert 'Service' in summary.resource_types
            assert 'ConfigMap' in summary.resource_types
            
        finally:
            Path(db_path).unlink()
    
    def test_get_namespaces(self):
        """Test getting namespace list."""
        db_path = create_test_database()
        
        try:
            client = DatabaseClient(db_path)
            namespaces = client.get_namespaces()
            
            assert isinstance(namespaces, list)
            assert 'default' in namespaces
            
        finally:
            Path(db_path).unlink()
    
    def test_get_resource_kinds(self):
        """Test getting resource kinds."""
        db_path = create_test_database()
        
        try:
            client = DatabaseClient(db_path)
            kinds = client.get_resource_kinds()
            
            assert isinstance(kinds, list)
            assert 'Pod' in kinds
            assert 'Service' in kinds
            assert 'ConfigMap' in kinds
            
        finally:
            Path(db_path).unlink()
    
    def test_search_resources(self):
        """Test resource search functionality."""
        db_path = create_test_database()
        
        try:
            client = DatabaseClient(db_path)
            results = client.search_resources('test')
            
            assert isinstance(results, list)
            assert len(results) >= 2  # Should find test-pod and test-service
            
            # Check result structure
            if results:
                result = results[0]
                assert 'name' in result
                assert 'namespace' in result
                assert 'kind' in result
                assert 'health_status' in result
            
        finally:
            Path(db_path).unlink()


def test_imports():
    """Test that all modules can be imported."""
    from k8s_reporter import DatabaseClient
    from k8s_reporter.models import ResourceSummary, ClusterOverview
    from k8s_reporter.database import DatabaseClient as DatabaseClientImport
    
    assert DatabaseClient is not None
    assert ResourceSummary is not None
    assert ClusterOverview is not None
    assert DatabaseClientImport is not None
