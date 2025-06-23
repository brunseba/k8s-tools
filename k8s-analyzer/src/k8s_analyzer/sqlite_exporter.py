"""
SQLite exporter for Kubernetes cluster data.

This module provides functionality to export parsed Kubernetes resources,
relationships, and health information to an SQLite database for analysis.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import ClusterState, KubernetesResource, Relationship, RelationshipType, HealthStatus

logger = logging.getLogger(__name__)


class SQLiteExporter:
    """Exports Kubernetes cluster data to SQLite database."""
    
    def __init__(self, db_path: Union[str, Path]):
        """Initialize SQLite exporter.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        
    def connect(self) -> None:
        """Establish database connection."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        logger.info(f"Connected to SQLite database: {self.db_path}")
        
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def create_schema(self) -> None:
        """Create database schema for Kubernetes data."""
        if not self.connection:
            raise RuntimeError("Database connection not established")
            
        cursor = self.connection.cursor()
        
        # Resources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT UNIQUE,
                name TEXT NOT NULL,
                namespace TEXT,
                kind TEXT NOT NULL,
                api_version TEXT NOT NULL,
                creation_timestamp DATETIME,
                deletion_timestamp DATETIME,
                resource_version TEXT,
                generation INTEGER,
                health_status TEXT NOT NULL,
                labels TEXT,  -- JSON
                annotations TEXT,  -- JSON
                spec TEXT,  -- JSON
                status TEXT,  -- JSON
                issues TEXT,  -- JSON array
                cluster_info TEXT,  -- JSON
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_uid TEXT NOT NULL,
                target_resource TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                source_name TEXT,
                source_namespace TEXT,
                source_kind TEXT,
                target_name TEXT,
                target_namespace TEXT,
                target_kind TEXT,
                description TEXT,
                strength REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_uid) REFERENCES resources (uid)
            )
        """)
        
        # Cluster info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cluster_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT,
                analysis_timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_timestamp DATETIME NOT NULL,
                total_resources INTEGER NOT NULL,
                total_relationships INTEGER NOT NULL,
                namespace_count INTEGER NOT NULL,
                resource_types TEXT,  -- JSON
                health_summary TEXT,  -- JSON
                namespaces TEXT,  -- JSON
                issues_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Resource health history (for tracking changes over time)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_health_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_uid TEXT NOT NULL,
                health_status TEXT NOT NULL,
                issues TEXT,  -- JSON array
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_uid) REFERENCES resources (uid)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_uid ON resources (uid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_kind ON resources (kind)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_namespace ON resources (namespace)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_health ON resources (health_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_uid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (relationship_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_history_uid ON resource_health_history (resource_uid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_health_history_timestamp ON resource_health_history (timestamp)")
        
        self.connection.commit()
        logger.info("Database schema created successfully")
        
    def export_cluster_state(self, cluster_state: ClusterState, replace_existing: bool = True) -> None:
        """Export complete cluster state to database.
        
        Args:
            cluster_state: The cluster state to export
            replace_existing: Whether to replace existing data or append
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
            
        logger.info(f"Exporting cluster state with {len(cluster_state.resources)} resources")
        
        if replace_existing:
            self._clear_existing_data()
            
        self._export_resources(cluster_state.resources)
        self._export_relationships(cluster_state.relationships)
        self._export_cluster_info(cluster_state.cluster_info, cluster_state.analysis_timestamp)
        self._export_analysis_summary(cluster_state)
        
        self.connection.commit()
        logger.info("Cluster state export completed successfully")
        
    def _clear_existing_data(self) -> None:
        """Clear existing data from all tables."""
        cursor = self.connection.cursor()
        tables = ["resource_health_history", "relationships", "resources", "cluster_info", "analysis_summary"]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            
        logger.info("Existing data cleared from database")
        
    def _export_resources(self, resources: List[KubernetesResource]) -> None:
        """Export resources to database."""
        cursor = self.connection.cursor()
        
        for resource in resources:
            # Convert complex fields to JSON
            labels_json = json.dumps(resource.metadata.labels) if resource.metadata.labels else None
            annotations_json = json.dumps(resource.metadata.annotations) if resource.metadata.annotations else None
            spec_json = json.dumps(resource.spec) if resource.spec else None
            status_json = json.dumps(resource.status) if resource.status else None
            issues_json = json.dumps(resource.issues) if resource.issues else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO resources (
                    uid, name, namespace, kind, api_version, creation_timestamp,
                    deletion_timestamp, resource_version, generation, health_status,
                    labels, annotations, spec, status, issues, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resource.metadata.uid,
                resource.metadata.name,
                resource.metadata.namespace,
                resource.kind,
                resource.api_version,
                resource.metadata.creation_timestamp,
                resource.metadata.deletion_timestamp,
                resource.metadata.resource_version,
                resource.metadata.generation,
                resource.health_status.value,
                labels_json,
                annotations_json,
                spec_json,
                status_json,
                issues_json,
                datetime.now()
            ))
            
            # Record health history
            if resource.metadata.uid:
                cursor.execute("""
                    INSERT INTO resource_health_history (
                        resource_uid, health_status, issues, timestamp
                    ) VALUES (?, ?, ?, ?)
                """, (
                    resource.metadata.uid,
                    resource.health_status.value,
                    issues_json,
                    datetime.now()
                ))
                
        logger.info(f"Exported {len(resources)} resources to database")
        
    def _export_relationships(self, relationships: List[Relationship]) -> None:
        """Export relationships to database."""
        cursor = self.connection.cursor()
        
        for rel in relationships:
            # Parse target to extract components
            target_parts = rel.target.split('/')
            target_kind = target_parts[0] if len(target_parts) > 0 else None
            target_name = target_parts[1] if len(target_parts) > 1 else None
            target_namespace = target_parts[2] if len(target_parts) > 2 else None
            
            cursor.execute("""
                INSERT INTO relationships (
                    source_uid, target_resource, relationship_type, source_name,
                    source_namespace, source_kind, target_name, target_namespace,
                    target_kind, description, strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rel.source_uid,
                rel.target,
                rel.relationship_type.value,
                rel.source_name,
                rel.source_namespace,
                rel.source_kind,
                target_name,
                target_namespace,
                target_kind,
                rel.description,
                rel.strength
            ))
            
        logger.info(f"Exported {len(relationships)} relationships to database")
        
    def _export_cluster_info(self, cluster_info: Dict[str, Any], timestamp: datetime) -> None:
        """Export cluster information to database."""
        cursor = self.connection.cursor()
        
        for key, value in cluster_info.items():
            value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            cursor.execute("""
                INSERT INTO cluster_info (key, value, analysis_timestamp)
                VALUES (?, ?, ?)
            """, (key, value_str, timestamp))
            
        logger.info(f"Exported {len(cluster_info)} cluster info items to database")
        
    def _export_analysis_summary(self, cluster_state: ClusterState) -> None:
        """Export analysis summary to database."""
        cursor = self.connection.cursor()
        
        summary = cluster_state.summary
        issues_count = sum(len(r.issues) for r in cluster_state.resources if r.issues)
        
        cursor.execute("""
            INSERT INTO analysis_summary (
                analysis_timestamp, total_resources, total_relationships,
                namespace_count, resource_types, health_summary, namespaces, issues_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cluster_state.analysis_timestamp,
            summary.get("total_resources", 0),
            summary.get("total_relationships", 0),
            len(summary.get("namespaces", {})),
            json.dumps(summary.get("resource_types", {})),
            json.dumps(summary.get("health_status", {})),
            json.dumps(list(summary.get("namespaces", {}).keys())),
            issues_count
        ))
        
        logger.info("Exported analysis summary to database")
        
    def query_resources(
        self,
        kind: Optional[str] = None,
        namespace: Optional[str] = None,
        health_status: Optional[str] = None,
        has_issues: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Query resources with filters.
        
        Args:
            kind: Filter by resource kind
            namespace: Filter by namespace
            health_status: Filter by health status
            has_issues: Filter resources with/without issues
            
        Returns:
            List of resource records
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
            
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM resources WHERE 1=1"
        params = []
        
        if kind:
            query += " AND kind = ?"
            params.append(kind)
            
        if namespace:
            query += " AND namespace = ?"
            params.append(namespace)
            
        if health_status:
            query += " AND health_status = ?"
            params.append(health_status)
            
        if has_issues is not None:
            if has_issues:
                query += " AND issues IS NOT NULL AND issues != '[]'"
            else:
                query += " AND (issues IS NULL OR issues = '[]')"
                
        query += " ORDER BY namespace, kind, name"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def query_relationships(
        self,
        source_kind: Optional[str] = None,
        target_kind: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query relationships with filters.
        
        Args:
            source_kind: Filter by source resource kind
            target_kind: Filter by target resource kind
            relationship_type: Filter by relationship type
            
        Returns:
            List of relationship records
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
            
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM relationships WHERE 1=1"
        params = []
        
        if source_kind:
            query += " AND source_kind = ?"
            params.append(source_kind)
            
        if target_kind:
            query += " AND target_kind = ?"
            params.append(target_kind)
            
        if relationship_type:
            query += " AND relationship_type = ?"
            params.append(relationship_type)
            
        query += " ORDER BY source_kind, source_name, relationship_type"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics.
        
        Returns:
            Dictionary with health statistics
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
            
        cursor = self.connection.cursor()
        
        # Get health status counts
        cursor.execute("""
            SELECT health_status, COUNT(*) as count
            FROM resources
            GROUP BY health_status
            ORDER BY health_status
        """)
        health_counts = {row['health_status']: row['count'] for row in cursor.fetchall()}
        
        # Get resources with issues
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM resources
            WHERE issues IS NOT NULL AND issues != '[]'
        """)
        issues_count = cursor.fetchone()['count']
        
        # Get namespace distribution
        cursor.execute("""
            SELECT namespace, COUNT(*) as count
            FROM resources
            WHERE namespace IS NOT NULL
            GROUP BY namespace
            ORDER BY count DESC
        """)
        namespace_counts = {row['namespace']: row['count'] for row in cursor.fetchall()}
        
        # Get resource type distribution
        cursor.execute("""
            SELECT kind, COUNT(*) as count
            FROM resources
            GROUP BY kind
            ORDER BY count DESC
        """)
        kind_counts = {row['kind']: row['count'] for row in cursor.fetchall()}
        
        return {
            "health_status": health_counts,
            "issues_count": issues_count,
            "namespace_distribution": namespace_counts,
            "resource_type_distribution": kind_counts,
            "total_resources": sum(health_counts.values()),
            "total_relationships": self._get_relationship_count()
        }
        
    def _get_relationship_count(self) -> int:
        """Get total relationship count."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM relationships")
        return cursor.fetchone()['count']
        
    def export_to_csv(self, output_dir: Union[str, Path]) -> None:
        """Export database contents to CSV files.
        
        Args:
            output_dir: Directory to save CSV files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.connection:
            raise RuntimeError("Database connection not established")
            
        # Export resources
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM resources ORDER BY namespace, kind, name")
        
        import csv
        
        with open(output_dir / "resources.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header
            columns = [description[0] for description in cursor.description]
            writer.writerow(columns)
            
            # Write data
            for row in cursor.fetchall():
                writer.writerow(row)
                
        # Export relationships
        cursor.execute("SELECT * FROM relationships ORDER BY source_kind, source_name")
        
        with open(output_dir / "relationships.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header
            columns = [description[0] for description in cursor.description]
            writer.writerow(columns)
            
            # Write data
            for row in cursor.fetchall():
                writer.writerow(row)
                
        logger.info(f"Exported database contents to CSV files in {output_dir}")


def export_cluster_to_sqlite(
    cluster_state: ClusterState,
    db_path: Union[str, Path],
    replace_existing: bool = True
) -> None:
    """Convenience function to export cluster state to SQLite.
    
    Args:
        cluster_state: The cluster state to export
        db_path: Path to SQLite database file
        replace_existing: Whether to replace existing data
    """
    with SQLiteExporter(db_path) as exporter:
        exporter.create_schema()
        exporter.export_cluster_state(cluster_state, replace_existing)
        
    logger.info(f"Cluster state exported to SQLite database: {db_path}")
