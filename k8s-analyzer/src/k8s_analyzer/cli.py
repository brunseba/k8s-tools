"""
CLI interface for Kubernetes Resource Analyzer.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.tree import Tree

from .analyzer import ResourceAnalyzer
from .models import ClusterState, RelationshipType
from .parser import parse_kubectl_export, discover_and_parse, find_kubernetes_files
from .sqlite_exporter import SQLiteExporter, export_cluster_to_sqlite

# Initialize CLI app and console
app = typer.Typer(
    name="k8s-analyzer",
    help="Kubernetes Resource Analyzer - Analyze kubectl exports and build resource relationships",
    no_args_is_help=True,
)
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


@app.command()
def parse(
    file_path: str = typer.Argument(..., help="Path to kubectl export file (JSON/YAML)"),
    additional_files: Optional[List[str]] = typer.Option(
        None, "--additional", "-a", help="Additional files to merge"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (JSON format)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Parse kubectl export files and extract resources."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Parsing kubectl export:[/bold blue] {file_path}")
    
    try:
        # Parse the files
        cluster_state = parse_kubectl_export(file_path, additional_files)
        
        # Display parsing results
        _display_parse_results(cluster_state)
        
        # Save output if requested
        if output:
            _save_cluster_state(cluster_state, output)
            console.print(f"[green]Results saved to:[/green] {output}")
        
    except Exception as e:
        console.print(f"[red]Error parsing files:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to kubectl export file (JSON/YAML)"),
    additional_files: Optional[List[str]] = typer.Option(
        None, "--additional", "-a", help="Additional files to merge"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (JSON format)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Parse and analyze kubectl exports with relationship mapping."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Analyzing kubectl export:[/bold blue] {file_path}")
    
    try:
        # Parse the files
        cluster_state = parse_kubectl_export(file_path, additional_files)
        
        # Analyze relationships
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Display analysis results
        _display_analysis_results(cluster_state)
        
        # Save output if requested
        if output:
            _save_cluster_state(cluster_state, output)
            console.print(f"[green]Analysis results saved to:[/green] {output}")
        
    except Exception as e:
        console.print(f"[red]Error analyzing files:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def report(
    file_path: str = typer.Argument(..., help="Path to kubectl export file (JSON/YAML)"),
    additional_files: Optional[List[str]] = typer.Option(
        None, "--additional", "-a", help="Additional files to merge"
    ),
    output: Optional[str] = typer.Option(
        "cluster-report.html", "--output", "-o", help="Output HTML report path"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Generate comprehensive analysis report."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Generating report for:[/bold blue] {file_path}")
    
    try:
        # Parse and analyze
        cluster_state = parse_kubectl_export(file_path, additional_files)
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Generate HTML report
        _generate_html_report(cluster_state, output)
        console.print(f"[green]Report generated:[/green] {output}")
        
    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def graph(
    file_path: str = typer.Argument(..., help="Path to kubectl export file (JSON/YAML)"),
    additional_files: Optional[List[str]] = typer.Option(
        None, "--additional", "-a", help="Additional files to merge"
    ),
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Filter by namespace"
    ),
    resource_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by resource type"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Display resource relationship graph."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Building relationship graph for:[/bold blue] {file_path}")
    
    try:
        # Parse and analyze
        cluster_state = parse_kubectl_export(file_path, additional_files)
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Display graph
        _display_relationship_graph(cluster_state, namespace, resource_type)
        
    except Exception as e:
        console.print(f"[red]Error building graph:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    file_path: str = typer.Argument(..., help="Path to kubectl export file (JSON/YAML)"),
    additional_files: Optional[List[str]] = typer.Option(
        None, "--additional", "-a", help="Additional files to merge"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Validate resource configurations and identify issues."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Validating configurations in:[/bold blue] {file_path}")
    
    try:
        # Parse and analyze
        cluster_state = parse_kubectl_export(file_path, additional_files)
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Display validation results
        _display_validation_results(cluster_state)
        
    except Exception as e:
        console.print(f"[red]Error validating configurations:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def scan(
    directory: str = typer.Argument(..., help="Directory to scan for Kubernetes files"),
    patterns: Optional[List[str]] = typer.Option(
        None, "--pattern", "-p", help="Glob patterns to match files (e.g., '*.yaml', 'deployment-*.json')"
    ),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Search recursively in subdirectories"),
    max_files: Optional[int] = typer.Option(None, "--max-files", "-m", help="Maximum number of files to process"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (JSON format)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Scan directory for Kubernetes files and parse them all."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Scanning directory:[/bold blue] {directory}")
    
    try:
        # Discover and parse files
        cluster_state = discover_and_parse(
            directory, 
            patterns=patterns, 
            recursive=recursive, 
            max_files=max_files
        )
        
        # Display results
        _display_parse_results(cluster_state)
        
        # Save output if requested
        if output:
            _save_cluster_state(cluster_state, output)
            console.print(f"[green]Results saved to:[/green] {output}")
        
    except Exception as e:
        console.print(f"[red]Error scanning directory:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def batch_analyze(
    directory: str = typer.Argument(..., help="Directory to scan for Kubernetes files"),
    patterns: Optional[List[str]] = typer.Option(
        None, "--pattern", "-p", help="Glob patterns to match files"
    ),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Search recursively in subdirectories"),
    max_files: Optional[int] = typer.Option(None, "--max-files", "-m", help="Maximum number of files to process"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (JSON format)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Scan directory, parse all Kubernetes files, and perform relationship analysis."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Batch analyzing directory:[/bold blue] {directory}")
    
    try:
        # Discover and parse files
        cluster_state = discover_and_parse(
            directory, 
            patterns=patterns, 
            recursive=recursive, 
            max_files=max_files
        )
        
        # Analyze relationships
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Display analysis results
        _display_analysis_results(cluster_state)
        
        # Save output if requested
        if output:
            _save_cluster_state(cluster_state, output)
            console.print(f"[green]Analysis results saved to:[/green] {output}")
        
    except Exception as e:
        console.print(f"[red]Error in batch analysis:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list_files(
    directory: str = typer.Argument(..., help="Directory to scan for Kubernetes files"),
    patterns: Optional[List[str]] = typer.Option(
        None, "--pattern", "-p", help="Glob patterns to match files"
    ),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Search recursively in subdirectories"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """List all Kubernetes files that would be processed in a directory."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Finding Kubernetes files in:[/bold blue] {directory}")
    
    try:
        # Find files
        files = find_kubernetes_files(directory, patterns=patterns, recursive=recursive)
        
        if not files:
            console.print("[yellow]No Kubernetes files found[/yellow]")
            return
        
        # Display files in a table
        table = Table(title=f"Found {len(files)} Kubernetes Files", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("File Path", style="cyan")
        table.add_column("Size", justify="right", style="green")
        table.add_column("Modified", style="yellow")
        
        for i, file_path in enumerate(files, 1):
            try:
                stat = file_path.stat()
                size = f"{stat.st_size:,} bytes"
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            except OSError:
                size = "Unknown"
                modified = "Unknown"
            
            table.add_row(str(i), str(file_path), size, modified)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing files:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export_sqlite(
    file_path: str = typer.Argument(..., help="Path to kubectl export file (JSON/YAML)"),
    db_path: str = typer.Argument(..., help="Path to SQLite database file"),
    additional_files: Optional[List[str]] = typer.Option(
        None, "--additional", "-a", help="Additional files to merge"
    ),
    replace: bool = typer.Option(True, "--replace/--append", help="Replace existing data or append"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Export analyzed cluster data to SQLite database."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Exporting to SQLite database:[/bold blue] {db_path}")
    
    try:
        # Parse and analyze
        cluster_state = parse_kubectl_export(file_path, additional_files)
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Export to SQLite
        export_cluster_to_sqlite(cluster_state, db_path, replace_existing=replace)
        
        console.print(f"[green]✓ Successfully exported to SQLite database:[/green] {db_path}")
        console.print(f"[dim]   Resources: {len(cluster_state.resources)}[/dim]")
        console.print(f"[dim]   Relationships: {len(cluster_state.relationships)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error exporting to SQLite:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export_multiple_sqlite(
    files: List[str] = typer.Argument(..., help="Multiple kubectl export files to process"),
    db_path: str = typer.Option(..., "--database", "-d", help="Path to SQLite database file"),
    replace: bool = typer.Option(True, "--replace/--append", help="Replace existing data or append"),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Number of files to process in each batch"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Export multiple kubectl export files to SQLite database with batch processing."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Exporting {len(files)} files to SQLite database:[/bold blue] {db_path}")
    
    if not files:
        console.print(f"[red]No files provided[/red]")
        raise typer.Exit(1)
    
    try:
        from .sqlite_exporter import export_multiple_files_to_sqlite
        
        # Export multiple files with progress reporting
        total_resources, total_relationships = export_multiple_files_to_sqlite(
            files, db_path, replace_existing=replace, batch_size=batch_size
        )
        
        console.print(f"[green]✓ Successfully exported {len(files)} files to SQLite database[/green]")
        console.print(f"[dim]   Total Resources: {total_resources}[/dim]")
        console.print(f"[dim]   Total Relationships: {total_relationships}[/dim]")
        console.print(f"[dim]   Database: {db_path}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error exporting multiple files to SQLite:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export_directory_sqlite(
    directory: str = typer.Argument(..., help="Directory to scan for Kubernetes files"),
    db_path: str = typer.Argument(..., help="Path to SQLite database file"),
    patterns: Optional[List[str]] = typer.Option(
        None, "--pattern", "-p", help="Glob patterns to match files"
    ),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Search recursively"),
    max_files: Optional[int] = typer.Option(None, "--max-files", "-m", help="Maximum number of files to process"),
    replace: bool = typer.Option(True, "--replace/--append", help="Replace existing data or append"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Scan directory and export all analyzed data to SQLite database."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Scanning and exporting directory to SQLite:[/bold blue] {directory}")
    console.print(f"[dim]Database: {db_path}[/dim]")
    
    try:
        # Discover, parse and analyze
        cluster_state = discover_and_parse(
            directory, 
            patterns=patterns, 
            recursive=recursive, 
            max_files=max_files
        )
        
        analyzer = ResourceAnalyzer()
        cluster_state = analyzer.analyze_cluster(cluster_state)
        
        # Export to SQLite
        export_cluster_to_sqlite(cluster_state, db_path, replace_existing=replace)
        
        console.print(f"[green]✓ Successfully exported directory analysis to SQLite database[/green]")
        console.print(f"[dim]   Resources: {len(cluster_state.resources)}[/dim]")
        console.print(f"[dim]   Relationships: {len(cluster_state.relationships)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error exporting directory to SQLite:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def query_db(
    db_path: str = typer.Argument(..., help="Path to SQLite database file"),
    resource_kind: Optional[str] = typer.Option(None, "--kind", "-k", help="Filter by resource kind"),
    namespace: Optional[str] = typer.Option(None, "--namespace", "-n", help="Filter by namespace"),
    health_status: Optional[str] = typer.Option(None, "--health", "-h", help="Filter by health status"),
    has_issues: Optional[bool] = typer.Option(None, "--issues/--no-issues", help="Filter resources with/without issues"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of results to show"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Query resources from SQLite database."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Querying SQLite database:[/bold blue] {db_path}")
    
    try:
        with SQLiteExporter(db_path) as db:
            # Query resources
            resources = db.query_resources(
                kind=resource_kind,
                namespace=namespace,
                health_status=health_status,
                has_issues=has_issues
            )
            
            if not resources:
                console.print("[yellow]No resources found matching the criteria[/yellow]")
                return
            
            # Display results in table
            table = Table(title=f"Query Results ({len(resources)} resources)", show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Namespace", style="blue")
            table.add_column("Kind", style="green")
            table.add_column("Health", style="yellow")
            table.add_column("Issues", style="red")
            
            for resource in resources[:limit]:
                # Parse issues JSON
                issues_count = 0
                if resource.get('issues'):
                    try:
                        import json
                        issues = json.loads(resource['issues'])
                        issues_count = len(issues) if issues else 0
                    except:
                        issues_count = 0
                
                # Health status styling
                health = resource['health_status']
                if health == 'healthy':
                    health_display = f"[green]{health}[/green]"
                elif health == 'warning':
                    health_display = f"[yellow]{health}[/yellow]"
                elif health == 'error':
                    health_display = f"[red]{health}[/red]"
                else:
                    health_display = health
                
                issues_display = f"[red]{issues_count}[/red]" if issues_count > 0 else "0"
                
                table.add_row(
                    resource['name'] or 'N/A',
                    resource['namespace'] or 'N/A',
                    resource['kind'],
                    health_display,
                    issues_display
                )
            
            console.print(table)
            
            if len(resources) > limit:
                console.print(f"[dim]Showing first {limit} of {len(resources)} results[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error querying database:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def db_summary(
    db_path: str = typer.Argument(..., help="Path to SQLite database file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Show summary statistics from SQLite database."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Database Summary:[/bold blue] {db_path}")
    
    try:
        with SQLiteExporter(db_path) as db:
            summary = db.get_health_summary()
            
            # Overall stats table
            stats_table = Table(title="Overall Statistics", show_header=True, header_style="bold magenta")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Count", justify="right", style="green")
            
            stats_table.add_row("Total Resources", str(summary['total_resources']))
            stats_table.add_row("Total Relationships", str(summary['total_relationships']))
            stats_table.add_row("Resources with Issues", str(summary['issues_count']))
            
            console.print(stats_table)
            
            # Health status table
            health_table = Table(title="Health Status Distribution", show_header=True, header_style="bold magenta")
            health_table.add_column("Status", style="cyan")
            health_table.add_column("Count", justify="right")
            
            for status, count in summary['health_status'].items():
                if status == 'healthy':
                    style = 'green'
                elif status == 'warning':
                    style = 'yellow'
                elif status == 'error':
                    style = 'red'
                else:
                    style = 'white'
                
                health_table.add_row(status.title(), f"[{style}]{count}[/{style}]")
            
            console.print(health_table)
            
            # Resource types table
            types_table = Table(title="Resource Type Distribution", show_header=True, header_style="bold magenta")
            types_table.add_column("Resource Type", style="cyan")
            types_table.add_column("Count", justify="right", style="green")
            
            for kind, count in list(summary['resource_type_distribution'].items())[:10]:
                types_table.add_row(kind, str(count))
            
            console.print(types_table)
            
            # Namespace distribution table (top 10)
            if summary['namespace_distribution']:
                ns_table = Table(title="Top Namespaces", show_header=True, header_style="bold magenta")
                ns_table.add_column("Namespace", style="cyan")
                ns_table.add_column("Resources", justify="right", style="green")
                
                for ns, count in list(summary['namespace_distribution'].items())[:10]:
                    ns_table.add_row(ns, str(count))
                
                console.print(ns_table)
        
    except Exception as e:
        console.print(f"[red]Error getting database summary:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export_csv(
    db_path: str = typer.Argument(..., help="Path to SQLite database file"),
    output_dir: str = typer.Argument(..., help="Directory to save CSV files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Export SQLite database contents to CSV files."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Exporting database to CSV:[/bold blue] {db_path}")
    console.print(f"[dim]Output directory: {output_dir}[/dim]")
    
    try:
        with SQLiteExporter(db_path) as db:
            db.export_to_csv(output_dir)
        
        console.print(f"[green]✓ Successfully exported database to CSV files in:[/green] {output_dir}")
        console.print(f"[dim]   Files: resources.csv, relationships.csv[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error exporting to CSV:[/red] {e}")
        raise typer.Exit(1)


def _display_parse_results(cluster_state: ClusterState) -> None:
    """Display parsing results."""
    summary = cluster_state.summary
    parse_stats = cluster_state.cluster_info.get("parse_stats", {})
    
    # Create summary table
    table = Table(title="Parse Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Total Resources", str(summary.get("total_resources", 0)))
    table.add_row("Namespaces", str(len(summary.get("namespaces", {}))))
    
    # Add parsing statistics
    if parse_stats:
        table.add_row("Parsed Successfully", str(parse_stats.get("parsed", 0)))
        if parse_stats.get("skipped", 0) > 0:
            table.add_row("Skipped Resources", f"[yellow]{parse_stats.get('skipped', 0)}[/yellow]")
        if parse_stats.get("errors", 0) > 0:
            table.add_row("Parse Errors", f"[red]{parse_stats.get('errors', 0)}[/red]")
    
    # Add resource type breakdown
    resource_types = summary.get("resource_types", {})
    for resource_type, count in sorted(resource_types.items()):
        table.add_row(f"  {resource_type}", str(count))
    
    console.print(table)
    
    # Display skipped kinds if any
    skipped_kinds = parse_stats.get("skipped_kinds", {})
    if skipped_kinds:
        skipped_table = Table(title="Skipped Kubernetes Kinds", show_header=True, header_style="bold yellow")
        skipped_table.add_column("Kind", style="cyan")
        skipped_table.add_column("Count", justify="right", style="yellow")
        skipped_table.add_column("Reason", style="dim")
        
        for kind, count in sorted(skipped_kinds.items()):
            skipped_table.add_row(kind, str(count), "Unsupported resource type")
        
        console.print(skipped_table)


def _display_analysis_results(cluster_state: ClusterState) -> None:
    """Display analysis results."""
    summary = cluster_state.summary
    parse_stats = cluster_state.cluster_info.get("parse_stats", {})
    
    # Debug: Print parse_stats to console
    if parse_stats:
        logger.debug(f"Parse stats found: {parse_stats}")
        # Force output of skipped kinds if any
        skipped_kinds = parse_stats.get("skipped_kinds", {})
        logger.info(f"DEBUG: Skipped kinds from parse_stats: {skipped_kinds}")
    
    # Summary table
    table = Table(title="Analysis Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Total Resources", str(summary.get("total_resources", 0)))
    table.add_row("Total Relationships", str(summary.get("total_relationships", 0)))
    table.add_row("Namespaces", str(len(summary.get("namespaces", {}))))
    
    # Add parsing statistics
    if parse_stats:
        table.add_row("Parsed Successfully", str(parse_stats.get("parsed", 0)))
        if parse_stats.get("skipped", 0) > 0:
            table.add_row("Skipped Resources", f"[yellow]{parse_stats.get('skipped', 0)}[/yellow]")
        if parse_stats.get("errors", 0) > 0:
            table.add_row("Parse Errors", f"[red]{parse_stats.get('errors', 0)}[/red]")
    
    console.print(table)
    
    # Health status table
    health_table = Table(title="Resource Health", show_header=True, header_style="bold magenta")
    health_table.add_column("Status", style="cyan")
    health_table.add_column("Count", justify="right")
    
    health_status = summary.get("health_status", {})
    for status, count in sorted(health_status.items()):
        if status == "healthy":
            style = "green"
        elif status == "warning":
            style = "yellow"
        elif status == "error":
            style = "red"
        else:
            style = "white"
        
        health_table.add_row(status.title(), f"[{style}]{count}[/{style}]")
    
    console.print(health_table)
    
    # Display skipped kinds if any
    skipped_kinds = parse_stats.get("skipped_kinds", {})
    if skipped_kinds:
        console.print()  # Add spacing
        skipped_table = Table(title="Skipped Kubernetes Kinds", show_header=True, header_style="bold yellow")
        skipped_table.add_column("Kind", style="cyan")
        skipped_table.add_column("Count", justify="right", style="yellow")
        skipped_table.add_column("Reason", style="dim")
        
        for kind, count in sorted(skipped_kinds.items()):
            skipped_table.add_row(kind, str(count), "Unsupported resource type")
        
        console.print(skipped_table)


def _display_relationship_graph(
    cluster_state: ClusterState, 
    namespace_filter: Optional[str] = None,
    resource_type_filter: Optional[str] = None,
) -> None:
    """Display relationship graph as a tree."""
    
    # Filter resources
    resources = cluster_state.resources
    if namespace_filter:
        resources = [r for r in resources if r.metadata.namespace == namespace_filter]
    if resource_type_filter:
        resources = [r for r in resources if r.kind == resource_type_filter]
    
    if not resources:
        console.print("[yellow]No resources match the filters[/yellow]")
        return
    
    # Create tree structure
    tree = Tree("[bold blue]Resource Relationships[/bold blue]")
    
    for resource in resources[:20]:  # Limit to first 20 for readability
        resource_node = tree.add(f"[cyan]{resource.full_name}[/cyan]")
        
        # Add relationships
        for relationship in resource.relationships:
            rel_style = _get_relationship_style(relationship.relationship_type)
            rel_text = f"[{rel_style}]{relationship.relationship_type.value}[/{rel_style}] {relationship.target}"
            resource_node.add(rel_text)
    
    console.print(tree)


def _display_validation_results(cluster_state: ClusterState) -> None:
    """Display validation results."""
    issues_found = []
    
    for resource in cluster_state.resources:
        if resource.issues:
            issues_found.append((resource, resource.issues))
    
    if not issues_found:
        console.print("[green]✓ No configuration issues found[/green]")
        return
    
    console.print(f"[red]Found {len(issues_found)} resources with issues:[/red]")
    
    for resource, issues in issues_found:
        console.print(f"\n[yellow]⚠️  {resource.full_name}[/yellow]")
        for issue in issues:
            console.print(f"   • {issue}")


def _get_relationship_style(relationship_type: RelationshipType) -> str:
    """Get color style for relationship type."""
    style_map = {
        RelationshipType.OWNS: "green",
        RelationshipType.USES: "blue",
        RelationshipType.EXPOSES: "magenta",
        RelationshipType.BINDS: "cyan",
        RelationshipType.REFERENCES: "yellow",
        RelationshipType.DEPENDS_ON: "red",
        RelationshipType.MANAGES: "green",
        RelationshipType.SELECTS: "blue",
    }
    return style_map.get(relationship_type, "white")


def _save_cluster_state(cluster_state: ClusterState, output_path: str) -> None:
    """Save cluster state to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON-serializable format
    data = cluster_state.model_dump(mode="json")
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _generate_html_report(cluster_state: ClusterState, output_path: str) -> None:
    """Generate HTML report."""
    # Simple HTML template for now
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kubernetes Cluster Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
            .resource {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007cba; }}
            .relationship {{ margin-left: 20px; color: #666; }}
            .issue {{ color: #d32f2f; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Kubernetes Cluster Analysis Report</h1>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Total Resources: {cluster_state.summary.get('total_resources', 0)}</p>
            <p>Total Relationships: {cluster_state.summary.get('total_relationships', 0)}</p>
            <p>Analysis Date: {cluster_state.analysis_timestamp.isoformat()}</p>
        </div>
        
        <h2>Resources</h2>
        <div id="resources">
    """
    
    for resource in cluster_state.resources[:50]:  # Limit for HTML size
        html_content += f"""
            <div class="resource">
                <h3>{resource.full_name}</h3>
                <p>Status: {resource.health_status.value}</p>
        """
        
        if resource.issues:
            for issue in resource.issues:
                html_content += f'<p class="issue">⚠️ {issue}</p>'
        
        if resource.relationships:
            html_content += "<h4>Relationships:</h4>"
            for rel in resource.relationships:
                html_content += f'<div class="relationship">→ {rel.relationship_type.value} {rel.target}</div>'
        
        html_content += "</div>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html_content, encoding="utf-8")


if __name__ == "__main__":
    app()
