#!/usr/bin/env python3
"""
Demonstration script for SQLite export capabilities.

This script shows how to use the k8s-analyzer to export Kubernetes cluster
data to SQLite and then query and analyze the data.
"""

import sys
from pathlib import Path

# Add the analyzer to path
sys.path.insert(0, str(Path(__file__).parent.parent / "k8s-analyzer" / "src"))

from k8s_analyzer.parser import discover_and_parse
from k8s_analyzer.analyzer import ResourceAnalyzer
from k8s_analyzer.sqlite_exporter import SQLiteExporter, export_cluster_to_sqlite


def main():
    """Main demonstration function."""
    print("🚀 Kubernetes Analyzer SQLite Export Demo")
    print("=" * 50)
    
    # Paths
    demo_dir = Path(__file__).parent / "multi-app-demo"
    db_path = Path(__file__).parent / "cluster_analysis.db"
    
    print(f"📁 Source directory: {demo_dir}")
    print(f"🗄️  Database file: {db_path}")
    print()
    
    # Step 1: Parse and analyze the demo Kubernetes files
    print("📋 Step 1: Parsing Kubernetes files...")
    try:
        cluster_state = discover_and_parse(demo_dir, recursive=True)
        print(f"   ✓ Found {len(cluster_state.resources)} resources")
        
        # Analyze relationships
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        print(f"   ✓ Identified {len(cluster_state.relationships)} relationships")
        
    except Exception as e:
        print(f"   ❌ Error parsing files: {e}")
        return
    
    print()
    
    # Step 2: Export to SQLite
    print("💾 Step 2: Exporting to SQLite database...")
    try:
        export_cluster_to_sqlite(cluster_state, db_path, replace_existing=True)
        print(f"   ✓ Successfully exported to {db_path}")
        
    except Exception as e:
        print(f"   ❌ Error exporting to database: {e}")
        return
    
    print()
    
    # Step 3: Query and analyze the database
    print("🔍 Step 3: Querying the database...")
    try:
        with SQLiteExporter(db_path) as db:
            # Get summary statistics
            print("\n📊 Database Summary:")
            summary = db.get_health_summary()
            print(f"   • Total Resources: {summary['total_resources']}")
            print(f"   • Total Relationships: {summary['total_relationships']}")
            print(f"   • Resources with Issues: {summary['issues_count']}")
            
            # Health status breakdown
            print("\n❤️  Health Status Distribution:")
            for status, count in summary['health_status'].items():
                emoji = {"healthy": "✅", "warning": "⚠️", "error": "❌"}.get(status, "ℹ️")
                print(f"   {emoji} {status.title()}: {count}")
            
            # Resource types
            print("\n📦 Resource Types:")
            for kind, count in summary['resource_type_distribution'].items():
                print(f"   • {kind}: {count}")
            
            # Namespaces
            print("\n🏠 Namespaces:")
            for ns, count in summary['namespace_distribution'].items():
                print(f"   • {ns}: {count} resources")
            
            print()
            
            # Query specific resources
            print("🔎 Sample Queries:")
            
            # All deployments
            deployments = db.query_resources(kind="Deployment")
            print(f"   • Found {len(deployments)} Deployments:")
            for dep in deployments:
                print(f"     - {dep['name']} (namespace: {dep['namespace']})")
            
            # All services
            services = db.query_resources(kind="Service")
            print(f"   • Found {len(services)} Services:")
            for svc in services:
                print(f"     - {svc['name']} (namespace: {svc['namespace']})")
            
            # Resources with issues
            issues_resources = db.query_resources(has_issues=True)
            if issues_resources:
                print(f"   • Found {len(issues_resources)} resources with issues:")
                for res in issues_resources:
                    print(f"     - {res['name']} ({res['kind']})")
            else:
                print("   • No resources with issues found ✅")
            
            # Relationships
            relationships = db.query_relationships()
            print(f"   • Found {len(relationships)} relationships:")
            for rel in relationships[:5]:  # Show first 5
                print(f"     - {rel['source_name']} ({rel['source_kind']}) "
                      f"{rel['relationship_type']} {rel['target_name'] or rel['target_resource']}")
            
    except Exception as e:
        print(f"   ❌ Error querying database: {e}")
        return
    
    print()
    
    # Step 4: Demonstrate CSV export
    print("📄 Step 4: Exporting to CSV...")
    try:
        csv_dir = Path(__file__).parent / "csv_export"
        csv_dir.mkdir(exist_ok=True)
        
        with SQLiteExporter(db_path) as db:
            db.export_to_csv(csv_dir)
        
        print(f"   ✓ CSV files exported to: {csv_dir}")
        
        # List generated files
        csv_files = list(csv_dir.glob("*.csv"))
        for csv_file in csv_files:
            size = csv_file.stat().st_size
            print(f"     - {csv_file.name} ({size:,} bytes)")
            
    except Exception as e:
        print(f"   ❌ Error exporting CSV: {e}")
        return
    
    print()
    
    # Step 5: Show some SQL examples
    print("💻 Step 5: SQL Query Examples:")
    print()
    print("   You can now use any SQLite client to query the database:")
    print(f"   sqlite3 {db_path}")
    print()
    print("   Example queries:")
    print("   ─" * 40)
    print("   -- Show all resources by type")
    print("   SELECT kind, COUNT(*) as count FROM resources GROUP BY kind;")
    print()
    print("   -- Show resources with issues")
    print("   SELECT name, kind, namespace, health_status")
    print("   FROM resources WHERE issues IS NOT NULL AND issues != '[]';")
    print()
    print("   -- Show service relationships")
    print("   SELECT source_name, relationship_type, target_resource")
    print("   FROM relationships WHERE source_kind = 'Service';")
    print()
    print("   -- Health status over time")
    print("   SELECT resource_uid, health_status, timestamp")
    print("   FROM resource_health_history ORDER BY timestamp DESC;")
    print()
    
    print("🎉 Demo completed successfully!")
    print(f"📁 Generated files:")
    print(f"   • SQLite database: {db_path}")
    print(f"   • CSV exports: {csv_dir}")
    print()
    print("💡 Next steps:")
    print("   • Use the CLI commands to export your own Kubernetes data")
    print("   • Query the database with SQLite tools or Python")
    print("   • Build custom dashboards and reports")
    print("   • Track resource health changes over time")


if __name__ == "__main__":
    main()
