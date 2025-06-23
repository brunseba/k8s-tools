#!/usr/bin/env python3
"""
Demonstration script for multiple file SQLite export capabilities.

This script shows how to export multiple Kubernetes files to SQLite
and perform advanced queries and analysis across the data.
"""

import sys
from pathlib import Path

# Add the analyzer to path
sys.path.insert(0, str(Path(__file__).parent.parent / "k8s-analyzer" / "src"))

from k8s_analyzer.sqlite_exporter import SQLiteExporter, export_multiple_files_to_sqlite


def main():
    """Main demonstration function."""
    print("🚀 Multiple File Kubernetes SQLite Export Demo")
    print("=" * 60)
    
    # Paths - use the actual input files
    inputs_dir = Path(__file__).parent.parent / "inputs" / "json"
    db_path = Path(__file__).parent / "multi_cluster_analysis.db"
    
    # Find available JSON files
    json_files = list(inputs_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != "cluster-report.html"]  # Exclude non-JSON
    
    print(f"📁 Source directory: {inputs_dir}")
    print(f"🗄️  Database file: {db_path}")
    print(f"📄 Found {len(json_files)} JSON files to process")
    print()
    
    # List the files we'll process
    print("📋 Files to process:")
    for i, file_path in enumerate(json_files, 1):
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   {i:2d}. {file_path.name:<25} ({size_mb:.1f} MB)")
    print()
    
    # Step 1: Export multiple files with batch processing
    print("💾 Step 1: Exporting multiple files to SQLite database...")
    try:
        total_resources, total_relationships = export_multiple_files_to_sqlite(
            json_files, 
            db_path, 
            replace_existing=True, 
            batch_size=3  # Process in batches of 3 files
        )
        
        print(f"   ✓ Successfully exported {len(json_files)} files")
        print(f"   ✓ Total Resources: {total_resources:,}")
        print(f"   ✓ Total Relationships: {total_relationships:,}")
        
    except Exception as e:
        print(f"   ❌ Error exporting files: {e}")
        return
    
    print()
    
    # Step 2: Advanced querying and analysis
    print("🔍 Step 2: Advanced querying and analysis...")
    try:
        with SQLiteExporter(db_path) as db:
            # Get comprehensive summary
            print("\n📊 Comprehensive Database Summary:")
            summary = db.get_health_summary()
            print(f"   • Total Resources: {summary['total_resources']:,}")
            print(f"   • Total Relationships: {summary['total_relationships']:,}")
            print(f"   • Resources with Issues: {summary['issues_count']:,}")
            
            # Health status breakdown
            print("\n❤️  Health Status Distribution:")
            for status, count in summary['health_status'].items():
                percentage = (count / summary['total_resources']) * 100
                emoji = {"healthy": "✅", "warning": "⚠️", "error": "❌"}.get(status, "ℹ️")
                print(f"   {emoji} {status.title()}: {count:,} ({percentage:.1f}%)")
            
            # Resource types analysis
            print("\n📦 Resource Type Analysis:")
            for kind, count in summary['resource_type_distribution'].items():
                percentage = (count / summary['total_resources']) * 100
                print(f"   • {kind:<20}: {count:>4,} ({percentage:>5.1f}%)")
            
            # Namespace analysis
            print("\n🏠 Top 10 Namespaces:")
            for ns, count in list(summary['namespace_distribution'].items())[:10]:
                percentage = (count / summary['total_resources']) * 100
                print(f"   • {ns:<35}: {count:>4,} ({percentage:>5.1f}%)")
            
            print()
            
            # Advanced queries
            print("🔎 Advanced Query Examples:")
            
            # Query 1: Find all pods with issues
            pods_with_issues = db.query_resources(kind="Pod", has_issues=True)
            print(f"   • Pods with issues: {len(pods_with_issues)}")
            if pods_with_issues:
                for pod in pods_with_issues[:3]:  # Show first 3
                    print(f"     - {pod['name'][:50]}... (namespace: {pod['namespace']})")
            
            # Query 2: Services by namespace
            services = db.query_resources(kind="Service")
            service_ns_count = {}
            for svc in services:
                ns = svc['namespace'] or 'cluster-scoped'
                service_ns_count[ns] = service_ns_count.get(ns, 0) + 1
            
            print(f"   • Services across namespaces: {len(service_ns_count)} namespaces")
            top_service_ns = sorted(service_ns_count.items(), key=lambda x: x[1], reverse=True)[:5]
            for ns, count in top_service_ns:
                print(f"     - {ns}: {count} services")
            
            # Query 3: ConfigMaps analysis
            configmaps = db.query_resources(kind="ConfigMap")
            cm_ns_count = {}
            for cm in configmaps:
                ns = cm['namespace'] or 'cluster-scoped'
                cm_ns_count[ns] = cm_ns_count.get(ns, 0) + 1
            
            print(f"   • ConfigMaps: {len(configmaps)} total")
            if cm_ns_count:
                max_ns = max(cm_ns_count.items(), key=lambda x: x[1])
                print(f"     - Highest concentration: {max_ns[0]} ({max_ns[1]} ConfigMaps)")
            
            # Query 4: Relationship analysis
            relationships = db.query_relationships()
            rel_types = {}
            for rel in relationships:
                rel_type = rel['relationship_type']
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            print(f"   • Relationship types found: {len(rel_types)}")
            for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
                print(f"     - {rel_type}: {count} relationships")
            
    except Exception as e:
        print(f"   ❌ Error querying database: {e}")
        return
    
    print()
    
    # Step 3: Generate insights
    print("💡 Step 3: Cluster Insights:")
    
    # Resource density analysis
    total_namespaces = len(summary['namespace_distribution'])
    avg_resources_per_ns = summary['total_resources'] / total_namespaces if total_namespaces > 0 else 0
    print(f"   • Average resources per namespace: {avg_resources_per_ns:.1f}")
    
    # Health ratio
    healthy_ratio = summary['health_status'].get('healthy', 0) / summary['total_resources'] * 100
    print(f"   • Cluster health ratio: {healthy_ratio:.1f}% healthy resources")
    
    # Complexity indicators
    relationship_density = summary['total_relationships'] / summary['total_resources']
    print(f"   • Relationship density: {relationship_density:.2f} relationships per resource")
    
    # Resource distribution
    configmap_ratio = summary['resource_type_distribution'].get('ConfigMap', 0) / summary['total_resources'] * 100
    print(f"   • Configuration density: {configmap_ratio:.1f}% ConfigMaps")
    
    print()
    
    # Step 4: Show SQL examples for external tools
    print("💻 Step 4: SQL Query Examples for External Tools:")
    print()
    print("   You can use any SQLite client to query the database:")
    print(f"   sqlite3 {db_path}")
    print()
    print("   Example advanced queries:")
    print("   ─" * 50)
    print("   -- Resource health by namespace")
    print("   SELECT namespace, health_status, COUNT(*) as count")
    print("   FROM resources")
    print("   WHERE namespace IS NOT NULL")
    print("   GROUP BY namespace, health_status")
    print("   ORDER BY namespace, health_status;")
    print()
    print("   -- Top namespaces by resource count")
    print("   SELECT namespace, COUNT(*) as resource_count")
    print("   FROM resources")
    print("   WHERE namespace IS NOT NULL")
    print("   GROUP BY namespace")
    print("   ORDER BY resource_count DESC")
    print("   LIMIT 10;")
    print()
    print("   -- Resources created in last 30 days")
    print("   SELECT kind, COUNT(*) as count")
    print("   FROM resources")
    print("   WHERE creation_timestamp > datetime('now', '-30 days')")
    print("   GROUP BY kind")
    print("   ORDER BY count DESC;")
    print()
    print("   -- Complex relationship analysis")
    print("   SELECT ")
    print("     r1.kind as source_kind,")
    print("     rel.relationship_type,")
    print("     r2.kind as target_kind,")
    print("     COUNT(*) as relationship_count")
    print("   FROM relationships rel")
    print("   JOIN resources r1 ON rel.source_uid = r1.uid")
    print("   JOIN resources r2 ON rel.target_name = r2.name")
    print("   GROUP BY r1.kind, rel.relationship_type, r2.kind")
    print("   ORDER BY relationship_count DESC;")
    print()
    
    print("🎉 Multi-file SQLite export demo completed successfully!")
    print(f"📁 Generated database: {db_path}")
    print(f"📊 Contains {total_resources:,} resources from {len(json_files)} files")
    print()
    print("💡 Next steps:")
    print("   • Use the CLI commands to export your own multi-file datasets")
    print("   • Query the database with SQL for custom analysis")
    print("   • Build dashboards and reports from the SQLite data")
    print("   • Integrate with BI tools for advanced visualization")
    print("   • Track cluster changes over time with multiple exports")


if __name__ == "__main__":
    main()
