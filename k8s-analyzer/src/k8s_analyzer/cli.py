"""
CLI interface for Kubernetes Resource Analyzer.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.tree import Tree

from .analyzer import ResourceAnalyzer
from .models import ClusterState, RelationshipType
from .parser import parse_kubectl_export

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


def _display_parse_results(cluster_state: ClusterState) -> None:
    """Display parsing results."""
    summary = cluster_state.summary
    
    # Create summary table
    table = Table(title="Parse Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Total Resources", str(summary.get("total_resources", 0)))
    table.add_row("Namespaces", str(len(summary.get("namespaces", {}))))
    
    # Add resource type breakdown
    resource_types = summary.get("resource_types", {})
    for resource_type, count in sorted(resource_types.items()):
        table.add_row(f"  {resource_type}", str(count))
    
    console.print(table)


def _display_analysis_results(cluster_state: ClusterState) -> None:
    """Display analysis results."""
    summary = cluster_state.summary
    
    # Summary table
    table = Table(title="Analysis Results", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    table.add_row("Total Resources", str(summary.get("total_resources", 0)))
    table.add_row("Total Relationships", str(summary.get("total_relationships", 0)))
    table.add_row("Namespaces", str(len(summary.get("namespaces", {}))))
    
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
