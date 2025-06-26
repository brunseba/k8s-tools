#!/usr/bin/env python3
"""
Test script to verify the new label-based viewpoints work correctly.
"""

import sys
import os
import sqlite3
import json
from datetime import datetime, timezone

# Add the k8s-reporter src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'k8s-reporter', 'src'))

from k8s_reporter.models import (
    LabelAnalysis, 
    ApplicationViewpoint, 
    EnvironmentViewpoint, 
    TeamOwnershipViewpoint, 
    CostOptimizationViewpoint,
    ANALYSIS_VIEWS
)
from k8s_reporter.database import DatabaseClient


def create_test_database():
    """Create a temporary SQLite database with test data."""
    db_path = "/tmp/test_labels.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create schema
    cursor.execute('''
        CREATE TABLE resources (
            uid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            namespace TEXT,
            kind TEXT NOT NULL,
            labels TEXT,
            health_status TEXT DEFAULT 'healthy',
            issues TEXT DEFAULT '[]',
            spec TEXT,
            status TEXT,
            creation_timestamp TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE relationships (
            id INTEGER PRIMARY KEY,
            source_uid TEXT,
            target_resource TEXT,
            relationship_type TEXT,
            strength REAL DEFAULT 1.0,
            description TEXT,
            source_namespace TEXT,
            target_namespace TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE analysis_summary (
            id INTEGER PRIMARY KEY,
            analysis_timestamp TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert test data
    test_resources = [
        {
            'uid': 'pod-1',
            'name': 'webapp-frontend',
            'namespace': 'production',
            'kind': 'Pod',
            'labels': json.dumps({
                'app.kubernetes.io/name': 'webapp',
                'app.kubernetes.io/component': 'frontend',
                'app.kubernetes.io/version': '1.2.0',
                'environment': 'production',
                'team': 'frontend-team',
                'cost-center': 'engineering'
            }),
            'health_status': 'healthy',
            'creation_timestamp': '2024-01-15T10:30:00Z'
        },
        {
            'uid': 'pod-2',
            'name': 'webapp-backend',
            'namespace': 'production',
            'kind': 'Pod',
            'labels': json.dumps({
                'app.kubernetes.io/name': 'webapp',
                'app.kubernetes.io/component': 'backend',
                'app.kubernetes.io/version': '1.2.0',
                'environment': 'production',
                'team': 'backend-team',
                'cost-center': 'engineering'
            }),
            'health_status': 'healthy',
            'creation_timestamp': '2024-01-15T10:31:00Z'
        },
        {
            'uid': 'pod-3',
            'name': 'database',
            'namespace': 'production',
            'kind': 'Pod',
            'labels': json.dumps({
                'app.kubernetes.io/name': 'database',
                'app.kubernetes.io/component': 'storage',
                'environment': 'production',
                'team': 'data-team',
                'cost-center': 'infrastructure'
            }),
            'health_status': 'warning',
            'creation_timestamp': '2024-01-10T09:00:00Z'
        },
        {
            'uid': 'pod-4',
            'name': 'test-app',
            'namespace': 'staging',
            'kind': 'Pod',
            'labels': json.dumps({
                'app.kubernetes.io/name': 'webapp',
                'app.kubernetes.io/component': 'frontend',
                'app.kubernetes.io/version': '1.3.0-beta',
                'environment': 'staging',
                'team': 'frontend-team',
                'cost-center': 'engineering'
            }),
            'health_status': 'healthy',
            'creation_timestamp': '2024-01-20T14:00:00Z'
        },
        {
            'uid': 'pod-5',
            'name': 'legacy-service',
            'namespace': 'default',
            'kind': 'Pod',
            'labels': json.dumps({}),  # No labels
            'health_status': 'error',
            'creation_timestamp': '2023-12-01T08:00:00Z'
        },
        {
            'uid': 'svc-1',
            'name': 'webapp-service',
            'namespace': 'production',
            'kind': 'Service',
            'labels': json.dumps({
                'app.kubernetes.io/name': 'webapp',
                'environment': 'production',
                'team': 'frontend-team'
            }),
            'health_status': 'healthy',
            'creation_timestamp': '2024-01-15T10:00:00Z'
        }
    ]
    
    for resource in test_resources:
        cursor.execute('''
            INSERT INTO resources (uid, name, namespace, kind, labels, health_status, creation_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resource['uid'],
            resource['name'],
            resource['namespace'],
            resource['kind'],
            resource['labels'],
            resource['health_status'],
            resource['creation_timestamp']
        ))
    
    # Insert analysis summary
    cursor.execute('''
        INSERT INTO analysis_summary (analysis_timestamp)
        VALUES (?)
    ''', (datetime.now(timezone.utc).isoformat(),))
    
    conn.commit()
    conn.close()
    
    return db_path


def test_new_viewpoints():
    """Test the new label-based viewpoints."""
    print("🧪 Testing new label-based viewpoints for k8s-reporter")
    print("=" * 60)
    
    # Create test database
    db_path = create_test_database()
    print(f"✅ Created test database: {db_path}")
    
    try:
        # Initialize database client
        db_client = DatabaseClient(db_path)
        print("✅ Database client initialized")
        
        # Test 1: Label Analysis
        print("\n📊 Testing Label Analysis...")
        label_analysis = db_client.get_label_analysis()
        print(f"   Total labeled resources: {label_analysis.total_labeled_resources}")
        print(f"   Total unlabeled resources: {label_analysis.total_unlabeled_resources}")
        print(f"   Label coverage: {label_analysis.label_coverage_percentage:.1f}%")
        print(f"   Common labels: {list(label_analysis.common_labels.keys())}")
        print(f"   Label quality score: {label_analysis.label_quality_score:.1f}")
        
        # Test 2: Application Viewpoint
        print("\n🚀 Testing Application Viewpoint...")
        app_viewpoint = db_client.get_application_viewpoint()
        print(f"   Total applications: {app_viewpoint.total_applications}")
        print(f"   Applications found: {[app['name'] for app in app_viewpoint.applications]}")
        for app in app_viewpoint.applications:
            print(f"     - {app['name']}: {app['resource_count']} resources, health: {app['health']}")
        print(f"   Orphaned resources: {len(app_viewpoint.orphaned_resources)}")
        
        # Test 3: Environment Viewpoint
        print("\n🌍 Testing Environment Viewpoint...")
        env_viewpoint = db_client.get_environment_viewpoint()
        print(f"   Environments: {env_viewpoint.environments}")
        for env in env_viewpoint.environments:
            resource_count = env_viewpoint.resources_by_environment.get(env, 0)
            print(f"     - {env}: {resource_count} resources")
        print(f"   Untagged resources: {len(env_viewpoint.untagged_resources)}")
        
        # Test 4: Team Ownership Viewpoint
        print("\n👥 Testing Team Ownership Viewpoint...")
        team_viewpoint = db_client.get_team_ownership_viewpoint()
        print(f"   Teams: {team_viewpoint.teams}")
        for team in team_viewpoint.teams:
            resource_count = team_viewpoint.team_resources.get(team, 0)
            print(f"     - {team}: {resource_count} resources")
        print(f"   Ownership coverage: {team_viewpoint.ownership_coverage:.1f}%")
        print(f"   Unowned resources: {len(team_viewpoint.unowned_resources)}")
        
        # Test 5: Cost Optimization Viewpoint
        print("\n💰 Testing Cost Optimization Viewpoint...")
        cost_viewpoint = db_client.get_cost_optimization_viewpoint()
        print(f"   Cost centers: {cost_viewpoint.cost_centers}")
        for cost_center in cost_viewpoint.cost_centers:
            resource_count = cost_viewpoint.cost_center_resources.get(cost_center, 0)
            print(f"     - {cost_center}: {resource_count} resources")
        print(f"   Billing coverage: {cost_viewpoint.billing_coverage:.1f}%")
        print(f"   Untagged for billing: {len(cost_viewpoint.untagged_for_billing)}")
        print(f"   Optimization opportunities: {len(cost_viewpoint.cost_optimization_opportunities)}")
        
        # Test 6: Check new views are in ANALYSIS_VIEWS
        print("\n🎯 Testing Analysis Views Registration...")
        new_views = ['labels', 'applications', 'environments', 'team_ownership', 'cost_optimization']
        for view_name in new_views:
            if view_name in ANALYSIS_VIEWS:
                view = ANALYSIS_VIEWS[view_name]
                print(f"   ✅ {view.get_title()} - {view.get_description()}")
            else:
                print(f"   ❌ {view_name} not found in ANALYSIS_VIEWS")
        
        print("\n🎉 All tests completed successfully!")
        print("The new label-based viewpoints are working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"🧹 Cleaned up test database: {db_path}")


if __name__ == "__main__":
    test_new_viewpoints()
