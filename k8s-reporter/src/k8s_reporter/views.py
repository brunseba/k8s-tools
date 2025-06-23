"""
Analysis views for k8s-reporter.

This module contains different view implementations for various analysis perspectives.
"""

import json
from datetime import datetime
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any

from k8s_reporter.database import DatabaseClient


def render_overview(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render cluster overview dashboard."""
    st.header("🏠 Cluster Overview")
    
    # Get overview data
    overview = db_client.get_cluster_overview()
    summary = db_client.get_resource_summary()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Resources",
            f"{overview.total_resources:,}",
            help="Total number of Kubernetes resources in the cluster"
        )
    
    with col2:
        st.metric(
            "Health Ratio",
            f"{overview.health_ratio:.1f}%",
            delta=f"{overview.health_ratio - 90:.1f}%" if overview.health_ratio < 90 else None,
            help="Percentage of healthy resources"
        )
    
    with col3:
        st.metric(
            "Namespaces", 
            overview.total_namespaces,
            help="Number of unique namespaces"
        )
    
    with col4:
        st.metric(
            "Issues",
            summary.issues_count,
            delta=-summary.issues_count if summary.issues_count > 0 else None,
            help="Resources with identified issues"
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Resource distribution pie chart
        st.subheader("📦 Resource Distribution")
        if overview.resource_distribution:
            # Limit to top 8 resource types for better visualization
            sorted_resources = sorted(overview.resource_distribution.items(), key=lambda x: x[1], reverse=True)
            top_resources = dict(sorted_resources[:8])
            
            if len(sorted_resources) > 8:
                other_count = sum(count for _, count in sorted_resources[8:])
                top_resources['Others'] = other_count
            
            fig_pie = px.pie(
                values=list(top_resources.values()),
                names=list(top_resources.keys()),
                title="Resource Types Distribution"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No resource data available")
    
    with col2:
        # Health status distribution
        st.subheader("❤️ Health Status")
        if summary.health_distribution:
            # Create color mapping for health status
            color_map = {
                'healthy': '#28a745',
                'warning': '#ffc107', 
                'error': '#dc3545',
                'unknown': '#6c757d'
            }
            
            health_data = pd.DataFrame([
                {'status': status, 'count': count}
                for status, count in summary.health_distribution.items()
            ])
            
            fig_bar = px.bar(
                health_data,
                x='status',
                y='count',
                title="Health Status Distribution",
                color='status',
                color_discrete_map=color_map
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No health data available")
    
    # Top namespaces table
    st.subheader("🏷️ Top Namespaces")
    if overview.top_namespaces:
        ns_data = pd.DataFrame(overview.top_namespaces)
        ns_data['percentage'] = (ns_data['count'] / overview.total_resources * 100).round(1)
        
        # Use st.dataframe with column configuration
        st.dataframe(
            ns_data.rename(columns={'name': 'Namespace', 'count': 'Resources', 'percentage': 'Percentage (%)'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No namespace data available")
    
    # Issues summary
    if overview.issues_summary:
        st.subheader("⚠️ Issues Summary")
        issues_data = pd.DataFrame([
            {'Status': status.title(), 'Count': count}
            for status, count in overview.issues_summary.items()
        ])
        
        if not issues_data.empty:
            fig_issues = px.bar(
                issues_data,
                x='Status',
                y='Count',
                title="Resources by Issue Type",
                color='Status',
                color_discrete_map={'Warning': '#ffc107', 'Error': '#dc3545'}
            )
            st.plotly_chart(fig_issues, use_container_width=True)


def render_security_analysis(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render security analysis dashboard."""
    st.header("🔒 Security Analysis")
    
    security = db_client.get_security_analysis()
    
    # Security metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Service Accounts",
            security.service_accounts_count,
            help="Total service accounts in the cluster"
        )
    
    with col2:
        st.metric(
            "Role Bindings",
            security.role_bindings_count,
            help="RBAC role bindings"
        )
    
    with col3:
        st.metric(
            "ConfigMaps",
            security.config_maps_count,
            help="Configuration storage objects"
        )
    
    with col4:
        st.metric(
            "Secrets",
            security.secrets_count,
            help="Secret storage objects"
        )
    
    # Pod security analysis
    st.subheader("🛡️ Pod Security Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Security context metrics
        st.metric(
            "Privileged Pods",
            security.privileged_pods,
            delta=-security.privileged_pods if security.privileged_pods > 0 else None,
            delta_color="inverse",
            help="Pods running with privileged access"
        )
        
        st.metric(
            "Root Containers",
            security.root_containers,
            delta=-security.root_containers if security.root_containers > 0 else None,
            delta_color="inverse",
            help="Containers running as root user"
        )
    
    with col2:
        st.metric(
            "No Security Context",
            security.pods_without_security_context,
            delta=-security.pods_without_security_context if security.pods_without_security_context > 0 else None,
            delta_color="inverse",
            help="Pods without security context configuration"
        )
    
    # Security recommendations
    st.subheader("📋 Security Recommendations")
    
    recommendations = []
    if security.privileged_pods > 0:
        recommendations.append(f"⚠️ **{security.privileged_pods} privileged pods** detected. Review if privileged access is necessary.")
    
    if security.root_containers > 0:
        recommendations.append(f"⚠️ **{security.root_containers} containers running as root**. Consider using non-root users.")
    
    if security.pods_without_security_context > 0:
        recommendations.append(f"⚠️ **{security.pods_without_security_context} pods without security context**. Add security context configurations.")
    
    if not recommendations:
        recommendations.append("✅ **Good job!** No major security issues detected in pod configurations.")
    
    for rec in recommendations:
        st.markdown(rec)


def render_namespace_analysis(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render namespace-specific analysis."""
    st.header("🏷️ Namespace Analysis")
    
    # Namespace selection
    namespaces = db_client.get_namespaces()
    
    if not namespaces:
        st.warning("No namespaces found in the database.")
        return
    
    # Use filter if provided, otherwise show selector
    if 'namespace' in filters:
        selected_namespace = filters['namespace']
        st.info(f"Analyzing namespace: **{selected_namespace}**")
    else:
        selected_namespace = st.selectbox("Select Namespace", namespaces)
    
    if not selected_namespace:
        return
    
    # Get namespace analysis
    analysis = db_client.get_namespace_analysis(selected_namespace)
    
    if not analysis:
        st.error(f"No data found for namespace: {selected_namespace}")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Resources", analysis.resource_count)
    
    with col2:
        st.metric("Resource Types", len(analysis.resource_types))
    
    with col3:
        st.metric("Relationships", analysis.relationships_count)
    
    with col4:
        st.metric("Issues", analysis.issues_count)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Resource types in namespace
        st.subheader("📦 Resource Types")
        if analysis.resource_types:
            fig = px.bar(
                x=list(analysis.resource_types.keys()),
                y=list(analysis.resource_types.values()),
                title=f"Resource Types in {selected_namespace}"
            )
            fig.update_layout(xaxis_title="Resource Type", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Health distribution
        st.subheader("❤️ Health Distribution")
        if analysis.health_distribution:
            color_map = {'healthy': '#28a745', 'warning': '#ffc107', 'error': '#dc3545'}
            
            fig = px.pie(
                values=list(analysis.health_distribution.values()),
                names=list(analysis.health_distribution.keys()),
                title=f"Health Status in {selected_namespace}",
                color=list(analysis.health_distribution.keys()),
                color_discrete_map=color_map
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Top resources table
    st.subheader("🔝 Top Resources")
    if analysis.top_resources:
        resources_df = pd.DataFrame(analysis.top_resources)
        resources_df['Health'] = resources_df['health'].apply(
            lambda x: f"{'🟢' if x == 'healthy' else '🟡' if x == 'warning' else '🔴'} {x.title()}"
        )
        
        st.dataframe(
            resources_df[['name', 'kind', 'Health']].rename(columns={
                'name': 'Resource Name',
                'kind': 'Kind',
                'Health': 'Health Status'
            }),
            use_container_width=True,
            hide_index=True
        )


def render_health_dashboard(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render health monitoring dashboard."""
    st.header("❤️ Health Dashboard")
    
    # Get health data
    summary = db_client.get_resource_summary()
    
    # Health overview metrics
    total_resources = summary.total_resources
    healthy_count = summary.health_distribution.get('healthy', 0)
    warning_count = summary.health_distribution.get('warning', 0)
    error_count = summary.health_distribution.get('error', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Resources",
            f"{total_resources:,}",
            help="Total resources monitored"
        )
    
    with col2:
        health_ratio = (healthy_count / total_resources * 100) if total_resources > 0 else 0
        st.metric(
            "Healthy",
            f"{healthy_count:,} ({health_ratio:.1f}%)",
            delta=f"{health_ratio:.1f}%",
            delta_color="normal",
            help="Resources in healthy state"
        )
    
    with col3:
        warning_ratio = (warning_count / total_resources * 100) if total_resources > 0 else 0
        st.metric(
            "Warnings",
            f"{warning_count:,} ({warning_ratio:.1f}%)",
            delta=f"-{warning_ratio:.1f}%" if warning_count > 0 else "0%",
            delta_color="inverse",
            help="Resources with warnings"
        )
    
    with col4:
        error_ratio = (error_count / total_resources * 100) if total_resources > 0 else 0
        st.metric(
            "Errors",
            f"{error_count:,} ({error_ratio:.1f}%)",
            delta=f"-{error_ratio:.1f}%" if error_count > 0 else "0%",
            delta_color="inverse",
            help="Resources with errors"
        )
    
    # Health trends over time
    st.subheader("📈 Health Trends")
    try:
        health_history = db_client.get_health_over_time()
        
        if not health_history.empty:
            fig = px.line(
                health_history,
                x='date',
                y='count',
                color='health_status',
                title="Health Status Over Time",
                color_discrete_map={
                    'healthy': '#28a745',
                    'warning': '#ffc107',
                    'error': '#dc3545'
                }
            )
            fig.update_layout(xaxis_title="Date", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical health data available")
    except Exception as e:
        st.info("Historical health data not available in this database")
    
    # Resources with issues
    if summary.issues_count > 0:
        st.subheader("⚠️ Resources with Issues")
        
        # Get resources with issues
        resources_df = db_client.get_resources_dataframe({'health_status': 'warning'})
        error_resources_df = db_client.get_resources_dataframe({'health_status': 'error'})
        
        if not resources_df.empty or not error_resources_df.empty:
            issues_df = pd.concat([resources_df, error_resources_df], ignore_index=True)
            
            # Display as table
            display_cols = ['name', 'namespace', 'kind', 'health_status']
            issues_display = issues_df[display_cols].copy()
            issues_display['health_status'] = issues_display['health_status'].apply(
                lambda x: f"{'🟡' if x == 'warning' else '🔴'} {x.title()}"
            )
            
            st.dataframe(
                issues_display.rename(columns={
                    'name': 'Resource Name',
                    'namespace': 'Namespace',
                    'kind': 'Kind',
                    'health_status': 'Status'
                }),
                use_container_width=True,
                hide_index=True
            )


def render_relationships_view(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render resource relationships analysis."""
    st.header("🔗 Resource Relationships")
    
    # Get relationships data
    relationships_df = db_client.get_relationships_dataframe(filters)
    
    if relationships_df.empty:
        st.warning("No relationships found in the database.")
        return
    
    # Relationships overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Relationships", len(relationships_df))
    
    with col2:
        unique_sources = relationships_df['source_kind'].nunique()
        st.metric("Source Types", unique_sources)
    
    with col3:
        unique_targets = relationships_df['target_kind'].nunique()
        st.metric("Target Types", unique_targets)
    
    # Relationship types distribution
    st.subheader("📊 Relationship Types")
    rel_types = relationships_df['relationship_type'].value_counts()
    
    if not rel_types.empty:
        fig = px.bar(
            x=rel_types.index,
            y=rel_types.values,
            title="Distribution of Relationship Types"
        )
        fig.update_layout(xaxis_title="Relationship Type", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Source-Target matrix
    st.subheader("🎯 Source-Target Matrix")
    if 'source_kind' in relationships_df.columns and 'target_kind' in relationships_df.columns:
        matrix_data = relationships_df.groupby(['source_kind', 'target_kind']).size().reset_index(name='count')
        
        if not matrix_data.empty:
            fig = px.scatter(
                matrix_data,
                x='source_kind',
                y='target_kind',
                size='count',
                title="Relationship Matrix (Source → Target)",
                hover_data=['count']
            )
            fig.update_layout(xaxis_title="Source Kind", yaxis_title="Target Kind")
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed relationships table
    st.subheader("📋 Relationship Details")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search relationships", placeholder="Enter resource name or type...")
    
    display_df = relationships_df.copy()
    if search_term:
        mask = (
            display_df['source_name'].str.contains(search_term, case=False, na=False) |
            display_df['target_name'].str.contains(search_term, case=False, na=False) |
            display_df['source_kind'].str.contains(search_term, case=False, na=False) |
            display_df['target_kind'].str.contains(search_term, case=False, na=False)
        )
        display_df = display_df[mask]
    
    # Display the table
    if not display_df.empty:
        # Select columns to display
        display_cols = ['source_name', 'source_kind', 'relationship_type', 'target_name', 'target_kind']
        if 'source_namespace' in display_df.columns:
            display_cols.insert(2, 'source_namespace')
        
        table_df = display_df[display_cols].head(100)  # Limit to 100 rows
        
        st.dataframe(
            table_df.rename(columns={
                'source_name': 'Source Name',
                'source_kind': 'Source Type',
                'source_namespace': 'Source Namespace',
                'relationship_type': 'Relationship',
                'target_name': 'Target Name',
                'target_kind': 'Target Type'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        if len(display_df) > 100:
            st.info(f"Showing first 100 of {len(display_df)} relationships")
    else:
        st.info("No relationships match your search criteria")


def render_namespace_components_view(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render detailed namespace components view with relationships."""
    st.header("🏗️ Namespace Components & Relationships")
    
    # Namespace selection
    namespaces = db_client.get_namespaces()
    
    if not namespaces:
        st.warning("No namespaces found in the database.")
        return
    
    # Use filter if provided, otherwise show selector
    if 'namespace' in filters:
        selected_namespace = filters['namespace']
        st.info(f"Analyzing components in namespace: **{selected_namespace}**")
    else:
        selected_namespace = st.selectbox("Select Namespace for Component Analysis", namespaces)
    
    if not selected_namespace:
        return
    
    # Get detailed components view
    components_view = db_client.get_namespace_components_view(selected_namespace)
    
    if not components_view:
        st.error(f"No components found in namespace: {selected_namespace}")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Components", components_view.total_components)
    
    with col2:
        st.metric("Component Types", len(components_view.component_groups))
    
    with col3:
        st.metric("Relationships", len(components_view.relationships))
    
    with col4:
        st.metric("Critical Components", len(components_view.critical_components))
    
    # Component groups visualization
    st.subheader("📦 Component Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Component types pie chart
        if components_view.component_groups:
            group_data = pd.DataFrame([
                {'type': kind, 'count': len(components)}
                for kind, components in components_view.component_groups.items()
            ])
            
            fig_pie = px.pie(
                group_data,
                values='count',
                names='type',
                title=f"Component Types in {selected_namespace}"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Health status distribution
        health_counts = {}
        for component in components_view.components:
            status = component.health_status
            health_counts[status] = health_counts.get(status, 0) + 1
        
        if health_counts:
            health_data = pd.DataFrame([
                {'status': status, 'count': count}
                for status, count in health_counts.items()
            ])
            
            color_map = {
                'healthy': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545',
                'unknown': '#6c757d'
            }
            
            fig_health = px.bar(
                health_data,
                x='status',
                y='count',
                title=f"Health Status Distribution",
                color='status',
                color_discrete_map=color_map
            )
            fig_health.update_layout(showlegend=False)
            st.plotly_chart(fig_health, use_container_width=True)
    
    # Relationships network visualization
    st.subheader("🔗 Component Relationships")
    
    if components_view.relationships:
        # Create network data for visualization
        nodes = set()
        edges = []
        
        for rel in components_view.relationships:
            nodes.add(rel.source_name)
            nodes.add(rel.target_name)
            edges.append({
                'source': rel.source_name,
                'target': rel.target_name,
                'relationship': rel.relationship_type,
                'strength': rel.strength
            })
        
        # Create a force-directed graph visualization
        import networkx as nx
        G = nx.DiGraph()
        
        # Add nodes with component type information
        component_types = {comp.name: comp.kind for comp in components_view.components}
        for node in nodes:
            G.add_node(node, kind=component_types.get(node, 'Unknown'))
        
        # Add edges
        for edge in edges:
            G.add_edge(edge['source'], edge['target'], 
                      relationship=edge['relationship'],
                      weight=edge['strength'])
        
        # Create layout
        try:
            pos = nx.spring_layout(G, k=3, iterations=50)
        except:
            pos = nx.random_layout(G)
        
        # Create plotly figure
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(G[edge[0]][edge[1]].get('relationship', 'UNKNOWN'))
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        
        # Color mapping for different component types
        kind_colors = {
            'Pod': '#1f77b4',
            'Service': '#ff7f0e', 
            'ConfigMap': '#2ca02c',
            'PersistentVolumeClaim': '#d62728',
            'Secret': '#9467bd',
            'Ingress': '#8c564b',
            'ServiceAccount': '#e377c2'
        }
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
            # Get component details
            component = next((c for c in components_view.components if c.name == node), None)
            if component:
                node_info.append(f"{component.name}<br>Type: {component.kind}<br>Health: {component.health_status}")
                node_colors.append(kind_colors.get(component.kind, '#636efa'))
            else:
                node_info.append(f"{node}<br>Type: Unknown")
                node_colors.append('#636efa')
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                size=20,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )
        
        fig_network = go.Figure(data=[edge_trace, node_trace],
                               layout=go.Layout(
                                   title=f"Component Relationships in {selected_namespace}",
                                   titlefont_size=16,
                                   showlegend=False,
                                   hovermode='closest',
                                   margin=dict(b=20,l=5,r=5,t=40),
                                   annotations=[ dict(
                                       text="Hover over components for details",
                                       showarrow=False,
                                       xref="paper", yref="paper",
                                       x=0.005, y=-0.002,
                                       xanchor="left", yanchor="bottom",
                                       font=dict(color="gray", size=12)
                                   )],
                                   xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                   yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                               ))
        
        st.plotly_chart(fig_network, use_container_width=True)
        
        # Relationship types summary
        st.subheader("📊 Relationship Types")
        rel_types = {}
        for rel in components_view.relationships:
            rel_types[rel.relationship_type] = rel_types.get(rel.relationship_type, 0) + 1
        
        if rel_types:
            rel_data = pd.DataFrame([
                {'type': rel_type, 'count': count}
                for rel_type, count in rel_types.items()
            ])
            
            fig_rel = px.bar(
                rel_data,
                x='type',
                y='count',
                title="Relationship Types Distribution",
                color='type'
            )
            fig_rel.update_layout(showlegend=False, xaxis_title="Relationship Type", yaxis_title="Count")
            st.plotly_chart(fig_rel, use_container_width=True)
    
    else:
        st.info("No relationships found between components in this namespace.")
    
    # Component details table
    st.subheader("📋 Component Details")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["All Components", "Critical Components", "Orphaned Components", "Dependency Chains"])
    
    with tab1:
        if components_view.components:
            components_data = []
            for comp in components_view.components:
                components_data.append({
                    'Name': comp.name,
                    'Type': comp.kind,
                    'Health': f"{'🟢' if comp.health_status == 'healthy' else '🟡' if comp.health_status == 'warning' else '🔴'} {comp.health_status.title()}",
                    'Issues': len(comp.issues),
                    'Labels': ', '.join([f"{k}={v}" for k, v in list(comp.labels.items())[:3]]) if comp.labels else 'None'
                })
            
            components_df = pd.DataFrame(components_data)
            st.dataframe(components_df, use_container_width=True, hide_index=True)
    
    with tab2:
        if components_view.critical_components:
            st.markdown(f"**{len(components_view.critical_components)} critical components** (3+ relationships):")
            for comp_name in components_view.critical_components:
                component = next((c for c in components_view.components if c.name == comp_name), None)
                if component:
                    status_icon = '🟢' if component.health_status == 'healthy' else '🟡' if component.health_status == 'warning' else '🔴'
                    st.markdown(f"- {status_icon} **{comp_name}** ({component.kind})")
        else:
            st.info("No critical components identified.")
    
    with tab3:
        if components_view.orphaned_components:
            st.markdown(f"**{len(components_view.orphaned_components)} orphaned components** (no relationships):")
            for comp_name in components_view.orphaned_components:
                component = next((c for c in components_view.components if c.name == comp_name), None)
                if component:
                    status_icon = '🟢' if component.health_status == 'healthy' else '🟡' if component.health_status == 'warning' else '🔴'
                    st.markdown(f"- {status_icon} **{comp_name}** ({component.kind})")
        else:
            st.info("All components have relationships.")
    
    with tab4:
        if components_view.dependency_chains:
            st.markdown(f"**{len(components_view.dependency_chains)} dependency chains identified:**")
            for i, chain in enumerate(components_view.dependency_chains, 1):
                chain_str = " → ".join(chain)
                st.markdown(f"{i}. {chain_str}")
        else:
            st.info("No dependency chains identified.")
    
    # Quick actions
    st.subheader("🔧 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Search Components"):
            search_term = st.text_input("Search components by name:")
            if search_term:
                matching_components = [
                    comp for comp in components_view.components 
                    if search_term.lower() in comp.name.lower()
                ]
                if matching_components:
                    st.write(f"Found {len(matching_components)} matching components:")
                    for comp in matching_components:
                        st.write(f"- {comp.name} ({comp.kind})")
                else:
                    st.write("No matching components found.")
    
    with col2:
        if st.button("📊 Export Component Data"):
            # Create export data
            export_data = {
                'components': [comp.dict() for comp in components_view.components],
                'relationships': [rel.dict() for rel in components_view.relationships],
                'summary': {
                    'namespace': components_view.namespace,
                    'total_components': components_view.total_components,
                    'critical_components': components_view.critical_components,
                    'orphaned_components': components_view.orphaned_components
                }
            }
            
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"{selected_namespace}_components.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🔄 Refresh Analysis"):
            st.rerun()


def render_storage_analysis(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render storage consumption analysis."""
    st.header("💾 Storage Analysis")
    
    # Get storage consumption data
    storage = db_client.get_storage_consumption()
    
    # Storage overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Volumes",
            storage.total_volumes,
            help="Total number of storage volumes (PV + PVC)"
        )
    
    with col2:
        st.metric(
            "Total Capacity",
            f"{storage.total_capacity_gb:.1f} GB",
            help="Total storage capacity across all volumes"
        )
    
    with col3:
        st.metric(
            "Utilization",
            f"{storage.utilization_percentage:.1f}%",
            delta=f"{storage.utilization_percentage - 70:.1f}%" if storage.utilization_percentage < 70 else None,
            help="Storage utilization percentage"
        )
    
    with col4:
        st.metric(
            "Issues",
            storage.unbound_pvcs + storage.orphaned_pvs,
            delta=-(storage.unbound_pvcs + storage.orphaned_pvs) if storage.unbound_pvcs + storage.orphaned_pvs > 0 else None,
            delta_color="inverse",
            help="Unbound PVCs and orphaned PVs"
        )
    
    # Storage distribution charts
    st.subheader("📈 Storage Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volumes by storage class
        if storage.volumes_by_class:
            class_data = pd.DataFrame([
                {'storage_class': sc, 'volume_count': count}
                for sc, count in storage.volumes_by_class.items()
            ])
            
            fig_volumes = px.pie(
                class_data,
                values='volume_count',
                names='storage_class',
                title="Volumes by Storage Class"
            )
            fig_volumes.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_volumes, use_container_width=True)
    
    with col2:
        # Capacity by storage class
        if storage.capacity_by_class:
            capacity_data = pd.DataFrame([
                {'storage_class': sc, 'capacity_gb': capacity}
                for sc, capacity in storage.capacity_by_class.items()
            ])
            
            fig_capacity = px.bar(
                capacity_data,
                x='storage_class',
                y='capacity_gb',
                title="Capacity by Storage Class (GB)",
                color='storage_class'
            )
            fig_capacity.update_layout(showlegend=False, xaxis_title="Storage Class", yaxis_title="Capacity (GB)")
            st.plotly_chart(fig_capacity, use_container_width=True)
    
    # Volume status analysis
    st.subheader("📊 Volume Status Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volume status distribution
        if storage.volumes_by_status:
            status_data = pd.DataFrame([
                {'status': status, 'count': count}
                for status, count in storage.volumes_by_status.items()
            ])
            
            color_map = {
                'bound': '#28a745',
                'available': '#17a2b8',
                'pending': '#ffc107',
                'failed': '#dc3545',
                'unknown': '#6c757d'
            }
            
            fig_status = px.bar(
                status_data,
                x='status',
                y='count',
                title="Volume Status Distribution",
                color='status',
                color_discrete_map=color_map
            )
            fig_status.update_layout(showlegend=False)
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Issue summary
        issue_data = {
            'Unbound PVCs': storage.unbound_pvcs,
            'Orphaned PVs': storage.orphaned_pvs,
            'Healthy Volumes': storage.total_volumes - storage.unbound_pvcs - storage.orphaned_pvs
        }
        
        if any(issue_data.values()):
            issue_df = pd.DataFrame([
                {'category': cat, 'count': count}
                for cat, count in issue_data.items()
            ])
            
            issue_colors = {
                'Unbound PVCs': '#ffc107',
                'Orphaned PVs': '#dc3545',
                'Healthy Volumes': '#28a745'
            }
            
            fig_issues = px.pie(
                issue_df,
                values='count',
                names='category',
                title="Storage Health Overview",
                color='category',
                color_discrete_map=issue_colors
            )
            st.plotly_chart(fig_issues, use_container_width=True)
    
    # Top consumers table
    st.subheader("🔝 Top Storage Consumers")
    
    if storage.top_consumers:
        consumers_data = []
        for volume in storage.top_consumers[:10]:
            consumers_data.append({
                'Name': volume.name,
                'Namespace': volume.namespace or 'cluster-wide',
                'Type': volume.kind,
                'Capacity': volume.capacity or 'Unknown',
                'Storage Class': volume.storage_class or 'default',
                'Status': f"{'🟢' if volume.status == 'bound' else '🟡' if volume.status == 'pending' else '🔴'} {volume.status.title()}",
                'Created': volume.created_at.strftime('%Y-%m-%d') if volume.created_at else 'Unknown'
            })
        
        consumers_df = pd.DataFrame(consumers_data)
        st.dataframe(consumers_df, use_container_width=True, hide_index=True)
    else:
        st.info("No storage volumes found.")
    
    # Per-namespace storage analysis
    st.subheader("🏷️ Per-Namespace Storage Analysis")
    
    namespaces = db_client.get_namespaces()
    if namespaces:
        selected_ns = st.selectbox("Select namespace for detailed storage analysis", 
                                  ['Select a namespace...'] + namespaces)
        
        if selected_ns and selected_ns != 'Select a namespace...':
            ns_storage = db_client.get_namespace_storage_analysis(selected_ns)
            
            if ns_storage:
                # Namespace storage metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Volumes", ns_storage.total_volumes)
                
                with col2:
                    st.metric("Capacity", f"{ns_storage.total_capacity_gb:.1f} GB")
                
                with col3:
                    st.metric("Storage Classes", len(ns_storage.storage_classes))
                
                with col4:
                    st.metric("Access Patterns", len(ns_storage.access_patterns))
                
                # Namespace storage details
                col1, col2 = st.columns(2)
                
                with col1:
                    if ns_storage.storage_classes:
                        st.write("**Storage Classes:**")
                        for sc, count in ns_storage.storage_classes.items():
                            st.write(f"- {sc}: {count} volumes")
                
                with col2:
                    if ns_storage.access_patterns:
                        st.write("**Access Patterns:**")
                        for pattern, count in ns_storage.access_patterns.items():
                            st.write(f"- {pattern}: {count} volumes")
                
                # Storage timeline for namespace
                st.write("**Storage Creation Timeline:**")
                timeline = db_client.get_namespace_storage_timeline(selected_ns)
                
                if timeline:
                    timeline_df = pd.DataFrame(timeline)
                    
                    # Create timeline chart
                    fig_timeline = px.scatter(
                        timeline_df,
                        x='date',
                        y='capacity_gb',
                        size='capacity_gb',
                        hover_data=['name', 'capacity'],
                        title=f"Storage Volume Creation Timeline - {selected_ns}",
                        labels={'date': 'Creation Date', 'capacity_gb': 'Capacity (GB)'}
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    # Timeline table
                    st.dataframe(
                        timeline_df[['date', 'time', 'name', 'capacity']].rename(columns={
                            'date': 'Date',
                            'time': 'Time',
                            'name': 'Volume Name',
                            'capacity': 'Capacity'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(f"No storage timeline data available for {selected_ns}")
            else:
                st.info(f"No storage volumes found in namespace {selected_ns}")
    
    # Storage recommendations
    st.subheader("📝 Storage Recommendations")
    
    recommendations = []
    
    if storage.unbound_pvcs > 0:
        recommendations.append(f"⚠️ **{storage.unbound_pvcs} unbound PVCs** detected. Check if storage classes are available and configured correctly.")
    
    if storage.orphaned_pvs > 0:
        recommendations.append(f"⚠️ **{storage.orphaned_pvs} orphaned PVs** found. Consider cleaning up unused persistent volumes to save costs.")
    
    if storage.utilization_percentage > 80:
        recommendations.append(f"⚠️ **High storage utilization** ({storage.utilization_percentage:.1f}%). Consider provisioning additional storage capacity.")
    
    if storage.utilization_percentage < 30:
        recommendations.append(f"💡 **Low storage utilization** ({storage.utilization_percentage:.1f}%). Review if all provisioned storage is necessary.")
    
    if not recommendations:
        recommendations.append("✅ **Storage health looks good!** No immediate issues detected.")
    
    for rec in recommendations:
        st.markdown(rec)


def render_temporal_analysis(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render temporal analysis of resource lifecycle."""
    st.header("⏰ Temporal Analysis")
    
    # Time range selector
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Analyze resource lifecycle patterns and creation trends over time**")
    
    with col2:
        days_back = st.selectbox(
            "Analysis Period",
            [7, 14, 30, 60, 90, 180],
            index=2,
            help="Number of days to look back for analysis"
        )
    
    # Get temporal analysis
    temporal = db_client.get_temporal_analysis(days_back)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Resources",
            temporal.total_resources,
            help="Total resources analyzed"
        )
    
    with col2:
        newest_count = len(temporal.newest_resources)
        st.metric(
            "New Resources",
            newest_count,
            delta=f"+{newest_count}" if newest_count > 0 else "0",
            help="Resources created in the last 7 days"
        )
    
    with col3:
        stale_count = len(temporal.stale_resources)
        st.metric(
            "Stale Resources",
            stale_count,
            delta=f"-{stale_count}" if stale_count > 0 else "0",
            delta_color="inverse",
            help="Resources older than 90 days"
        )
    
    with col4:
        active_namespaces = len(temporal.most_active_namespaces)
        st.metric(
            "Active Namespaces",
            active_namespaces,
            help="Namespaces with resource activity"
        )
    
    # Resource creation timeline
    st.subheader("📈 Resource Creation Timeline")
    
    if temporal.creation_timeline:
        # Prepare timeline data for visualization
        timeline_df = pd.DataFrame(temporal.creation_timeline)
        
        # Create main timeline chart
        fig_timeline = px.line(
            timeline_df,
            x='date',
            y='total',
            title=f"Daily Resource Creation - Last {days_back} Days",
            labels={'date': 'Date', 'total': 'Resources Created'}
        )
        fig_timeline.update_traces(mode='lines+markers')
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Resource creation by type over time
        if any(entry.get('by_kind') for entry in temporal.creation_timeline):
            # Flatten the by_kind data
            kind_timeline = []
            for entry in temporal.creation_timeline:
                for kind, count in entry.get('by_kind', {}).items():
                    kind_timeline.append({
                        'date': entry['date'],
                        'kind': kind,
                        'count': count
                    })
            
            if kind_timeline:
                kind_df = pd.DataFrame(kind_timeline)
                
                fig_kind_timeline = px.line(
                    kind_df,
                    x='date',
                    y='count',
                    color='kind',
                    title="Resource Creation by Type Over Time",
                    labels={'date': 'Date', 'count': 'Count', 'kind': 'Resource Type'}
                )
                st.plotly_chart(fig_kind_timeline, use_container_width=True)
    else:
        st.info("No timeline data available for the selected period.")
    
    # Age distribution analysis
    st.subheader("📋 Resource Age Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution pie chart
        if temporal.age_distribution:
            age_data = pd.DataFrame([
                {'age_group': group, 'count': count}
                for group, count in temporal.age_distribution.items()
                if count > 0
            ])
            
            if not age_data.empty:
                fig_age = px.pie(
                    age_data,
                    values='count',
                    names='age_group',
                    title="Resource Age Distribution"
                )
                fig_age.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # Creation patterns (day of week)
        if temporal.creation_patterns:
            # Order days of week properly
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pattern_data = []
            
            for day in days_order:
                count = temporal.creation_patterns.get(day, 0)
                pattern_data.append({'day': day, 'count': count})
            
            pattern_df = pd.DataFrame(pattern_data)
            
            fig_patterns = px.bar(
                pattern_df,
                x='day',
                y='count',
                title="Resource Creation by Day of Week",
                color='count',
                color_continuous_scale='viridis'
            )
            fig_patterns.update_layout(showlegend=False, xaxis_title="Day of Week", yaxis_title="Resources Created")
            st.plotly_chart(fig_patterns, use_container_width=True)
    
    # Most active namespaces
    st.subheader("🏷️ Most Active Namespaces")
    
    if temporal.most_active_namespaces:
        ns_data = pd.DataFrame(temporal.most_active_namespaces[:10])
        
        fig_namespaces = px.bar(
            ns_data,
            x='namespace',
            y='resource_count',
            title="Resource Count by Namespace",
            color='resource_count',
            color_continuous_scale='blues'
        )
        fig_namespaces.update_layout(showlegend=False, xaxis_title="Namespace", yaxis_title="Resource Count")
        st.plotly_chart(fig_namespaces, use_container_width=True)
    
    # Resource lifecycle statistics
    st.subheader("📉 Resource Lifecycle Statistics")
    
    if temporal.resource_lifecycle_stats:
        lifecycle_data = []
        for kind, stats in temporal.resource_lifecycle_stats.items():
            lifecycle_data.append({
                'Resource Type': kind,
                'Count': stats['count'],
                'Avg Age (days)': f"{stats['avg_age']:.1f}",
                'Min Age (days)': stats.get('min_age', 0),
                'Max Age (days)': stats.get('max_age', 0)
            })
        
        lifecycle_df = pd.DataFrame(lifecycle_data)
        lifecycle_df = lifecycle_df.sort_values('Count', ascending=False)
        
        st.dataframe(lifecycle_df, use_container_width=True, hide_index=True)
    
    # Resource details tables
    st.subheader("📋 Resource Details")
    
    # Create tabs for different resource categories
    tab1, tab2, tab3 = st.tabs(["Newest Resources", "Oldest Resources", "Stale Resources"])
    
    with tab1:
        if temporal.newest_resources:
            newest_data = []
            for resource in temporal.newest_resources:
                newest_data.append({
                    'Name': resource.resource_name,
                    'Type': resource.resource_kind,
                    'Namespace': resource.namespace or 'cluster-wide',
                    'Age (days)': f"{resource.age_days:.1f}",
                    'Created': resource.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Stage': resource.lifecycle_stage.title()
                })
            
            newest_df = pd.DataFrame(newest_data)
            st.dataframe(newest_df, use_container_width=True, hide_index=True)
        else:
            st.info("No new resources in the selected time period.")
    
    with tab2:
        if temporal.oldest_resources:
            oldest_data = []
            for resource in temporal.oldest_resources:
                oldest_data.append({
                    'Name': resource.resource_name,
                    'Type': resource.resource_kind,
                    'Namespace': resource.namespace or 'cluster-wide',
                    'Age (days)': f"{resource.age_days:.0f}",
                    'Created': resource.created_at.strftime('%Y-%m-%d'),
                    'Stage': resource.lifecycle_stage.title()
                })
            
            oldest_df = pd.DataFrame(oldest_data)
            st.dataframe(oldest_df, use_container_width=True, hide_index=True)
        else:
            st.info("No old resources found.")
    
    with tab3:
        if temporal.stale_resources:
            stale_data = []
            for resource in temporal.stale_resources:
                stale_data.append({
                    'Name': resource.resource_name,
                    'Type': resource.resource_kind,
                    'Namespace': resource.namespace or 'cluster-wide',
                    'Age (days)': f"{resource.age_days:.0f}",
                    'Created': resource.created_at.strftime('%Y-%m-%d'),
                    'Stage': resource.lifecycle_stage.title()
                })
            
            stale_df = pd.DataFrame(stale_data)
            st.dataframe(stale_df, use_container_width=True, hide_index=True)
            
            st.warning("⚠️ Consider reviewing these stale resources for potential cleanup or archival.")
        else:
            st.success("✅ No stale resources found! All resources are relatively recent.")


def render_resource_efficiency(db_client: DatabaseClient, filters: Dict[str, Any]):
    """Render resource efficiency analysis with Pod resource issues."""
    st.header("⚡ Resource Efficiency Analysis")
    
    # Get resource efficiency data
    efficiency = db_client.get_resource_efficiency()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Pods Analyzed",
            efficiency.total_pods_analyzed,
            help="Total number of pods examined for resource configuration"
        )
    
    with col2:
        st.metric(
            "Resource Coverage",
            f"{efficiency.resource_coverage_percentage:.1f}%",
            delta=f"{efficiency.resource_coverage_percentage - 80:.1f}%" if efficiency.resource_coverage_percentage < 80 else None,
            help="Percentage of pods with complete resource requests and limits"
        )
    
    with col3:
        st.metric(
            "Problematic Pods",
            len(efficiency.problematic_pods),
            delta=-len(efficiency.problematic_pods) if len(efficiency.problematic_pods) > 0 else None,
            delta_color="inverse",
            help="Pods with missing resource requests or limits"
        )
    
    with col4:
        critical_pods = len([p for p in efficiency.problematic_pods if p.issue_severity == 'critical'])
        st.metric(
            "Critical Issues",
            critical_pods,
            delta=-critical_pods if critical_pods > 0 else None,
            delta_color="inverse",
            help="Pods with no resource constraints at all"
        )
    
    # Resource configuration issues breakdown
    st.subheader("📊 Resource Configuration Issues")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pod resource issues pie chart
        issue_data = {
            'Complete Resources': efficiency.total_pods_analyzed - len(efficiency.problematic_pods),
            'Missing Requests': efficiency.pods_without_requests,
            'Missing Limits': efficiency.pods_without_limits,
            'No Resources': efficiency.pods_without_any_resources
        }
        
        if any(issue_data.values()):
            issue_df = pd.DataFrame([
                {'category': cat, 'count': count}
                for cat, count in issue_data.items()
                if count > 0
            ])
            
            issue_colors = {
                'Complete Resources': '#28a745',
                'Missing Requests': '#ffc107',
                'Missing Limits': '#fd7e14',
                'No Resources': '#dc3545'
            }
            
            fig_issues = px.pie(
                issue_df,
                values='count',
                names='category',
                title="Pod Resource Configuration Status",
                color='category',
                color_discrete_map=issue_colors
            )
            st.plotly_chart(fig_issues, use_container_width=True)
    
    with col2:
        # Severity distribution
        if efficiency.problematic_pods:
            severity_counts = {}
            for pod in efficiency.problematic_pods:
                severity_counts[pod.issue_severity] = severity_counts.get(pod.issue_severity, 0) + 1
            
            severity_data = pd.DataFrame([
                {'severity': sev, 'count': count}
                for sev, count in severity_counts.items()
            ])
            
            severity_colors = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#17a2b8'
            }
            
            fig_severity = px.bar(
                severity_data,
                x='severity',
                y='count',
                title="Issue Severity Distribution",
                color='severity',
                color_discrete_map=severity_colors
            )
            fig_severity.update_layout(showlegend=False)
            st.plotly_chart(fig_severity, use_container_width=True)
    
    # Problematic pods detailed analysis
    st.subheader("🚨 Pods with Resource Issues")
    
    if efficiency.problematic_pods:
        # Create tabs for different severity levels
        critical_pods = [p for p in efficiency.problematic_pods if p.issue_severity == 'critical']
        high_pods = [p for p in efficiency.problematic_pods if p.issue_severity == 'high']
        medium_pods = [p for p in efficiency.problematic_pods if p.issue_severity == 'medium']
        low_pods = [p for p in efficiency.problematic_pods if p.issue_severity == 'low']
        
        tabs = []
        if critical_pods:
            tabs.append(f"Critical ({len(critical_pods)})")
        if high_pods:
            tabs.append(f"High ({len(high_pods)})")
        if medium_pods:
            tabs.append(f"Medium ({len(medium_pods)})")
        if low_pods:
            tabs.append(f"Low ({len(low_pods)})")
        tabs.append("All Issues")
        
        tab_objects = st.tabs(tabs)
        tab_index = 0
        
        # Critical issues tab
        if critical_pods:
            with tab_objects[tab_index]:
                st.error(f"🚨 **{len(critical_pods)} pods with CRITICAL resource issues** - No resource constraints defined!")
                
                for pod in critical_pods[:10]:  # Show top 10
                    with st.expander(f"🔴 {pod.name} ({pod.namespace})", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Namespace:** {pod.namespace}")
                            st.write(f"**Health Status:** {pod.health_status}")
                            st.write(f"**Containers:** {', '.join(pod.containers)}")
                            if pod.created_at:
                                st.write(f"**Created:** {pod.created_at.strftime('%Y-%m-%d %H:%M')}")
                        
                        with col2:
                            st.write(f"**Missing Requests:** {', '.join(pod.missing_requests) if pod.missing_requests else 'None'}")
                            st.write(f"**Missing Limits:** {', '.join(pod.missing_limits) if pod.missing_limits else 'None'}")
                        
                        st.write("**Recommendations:**")
                        for rec in pod.recommendations:
                            st.write(f"- {rec}")
                
                if len(critical_pods) > 10:
                    st.info(f"Showing 10 of {len(critical_pods)} critical pods. Use filters to see more.")
            tab_index += 1
        
        # High issues tab
        if high_pods:
            with tab_objects[tab_index]:
                st.warning(f"⚠️ **{len(high_pods)} pods with HIGH priority resource issues**")
                
                high_data = []
                for pod in high_pods:
                    high_data.append({
                        'Pod Name': pod.name,
                        'Namespace': pod.namespace,
                        'Missing Requests': ', '.join(pod.missing_requests) if pod.missing_requests else '✅',
                        'Missing Limits': ', '.join(pod.missing_limits) if pod.missing_limits else '✅',
                        'Health': f"{'🟢' if pod.health_status == 'healthy' else '🟡' if pod.health_status == 'warning' else '🔴'} {pod.health_status.title()}",
                        'Containers': len(pod.containers)
                    })
                
                if high_data:
                    high_df = pd.DataFrame(high_data)
                    st.dataframe(high_df, use_container_width=True, hide_index=True)
            tab_index += 1
        
        # Medium issues tab
        if medium_pods:
            with tab_objects[tab_index]:
                st.info(f"ℹ️ **{len(medium_pods)} pods with MEDIUM priority resource issues**")
                
                medium_data = []
                for pod in medium_pods:
                    medium_data.append({
                        'Pod Name': pod.name,
                        'Namespace': pod.namespace,
                        'Missing Requests': ', '.join(pod.missing_requests) if pod.missing_requests else '✅',
                        'Missing Limits': ', '.join(pod.missing_limits) if pod.missing_limits else '✅',
                        'Health': f"{'🟢' if pod.health_status == 'healthy' else '🟡' if pod.health_status == 'warning' else '🔴'} {pod.health_status.title()}",
                    })
                
                if medium_data:
                    medium_df = pd.DataFrame(medium_data)
                    st.dataframe(medium_df, use_container_width=True, hide_index=True)
            tab_index += 1
        
        # Low issues tab
        if low_pods:
            with tab_objects[tab_index]:
                st.success(f"📝 **{len(low_pods)} pods with LOW priority resource issues**")
                
                low_data = []
                for pod in low_pods:
                    low_data.append({
                        'Pod Name': pod.name,
                        'Namespace': pod.namespace,
                        'Missing Requests': ', '.join(pod.missing_requests) if pod.missing_requests else '✅',
                        'Missing Limits': ', '.join(pod.missing_limits) if pod.missing_limits else '✅',
                    })
                
                if low_data:
                    low_df = pd.DataFrame(low_data)
                    st.dataframe(low_df, use_container_width=True, hide_index=True)
            tab_index += 1
        
        # All issues tab
        with tab_objects[tab_index]:
            st.subheader("Complete Resource Issues Overview")
            
            all_issues_data = []
            for pod in efficiency.problematic_pods:
                severity_icon = {
                    'critical': '🚨',
                    'high': '⚠️', 
                    'medium': 'ℹ️',
                    'low': '📝'
                }.get(pod.issue_severity, '❓')
                
                all_issues_data.append({
                    'Severity': f"{severity_icon} {pod.issue_severity.title()}",
                    'Pod Name': pod.name,
                    'Namespace': pod.namespace,
                    'Missing Requests': ', '.join(pod.missing_requests) if pod.missing_requests else '✅',
                    'Missing Limits': ', '.join(pod.missing_limits) if pod.missing_limits else '✅',
                    'Health': f"{'🟢' if pod.health_status == 'healthy' else '🟡' if pod.health_status == 'warning' else '🔴'} {pod.health_status.title()}",
                    'Containers': len(pod.containers)
                })
            
            if all_issues_data:
                all_df = pd.DataFrame(all_issues_data)
                st.dataframe(all_df, use_container_width=True, hide_index=True)
    
    else:
        st.success("🎉 **Excellent!** All pods have proper resource requests and limits configured.")
    
    # Additional efficiency metrics
    st.subheader("📈 Additional Efficiency Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Unused ConfigMaps",
            efficiency.unused_config_maps,
            delta=-efficiency.unused_config_maps if efficiency.unused_config_maps > 0 else None,
            delta_color="inverse",
            help="ConfigMaps not referenced by any resources"
        )
    
    with col2:
        st.metric(
            "Orphaned PVCs",
            efficiency.orphaned_pvcs,
            delta=-efficiency.orphaned_pvcs if efficiency.orphaned_pvcs > 0 else None,
            delta_color="inverse",
            help="PersistentVolumeClaims in pending state"
        )
    
    with col3:
        st.metric(
            "Services Analysis",
            efficiency.services_without_endpoints,
            help="Services without proper endpoints (requires deeper analysis)"
        )
    
    # Resource optimization recommendations
    st.subheader("💡 Resource Optimization Recommendations")
    
    recommendations = []
    
    if efficiency.pods_without_any_resources > 0:
        recommendations.append(
            f"🚨 **CRITICAL**: {efficiency.pods_without_any_resources} pods have NO resource constraints. "
            "This can cause cluster instability and resource starvation. Add requests and limits immediately."
        )
    
    if efficiency.pods_without_requests > 0:
        recommendations.append(
            f"⚠️ **{efficiency.pods_without_requests} pods missing resource requests**. "
            "Add CPU and memory requests to ensure proper scheduling and prevent resource contention."
        )
    
    if efficiency.pods_without_limits > 0:
        recommendations.append(
            f"⚠️ **{efficiency.pods_without_limits} pods missing resource limits**. "
            "Add CPU and memory limits to prevent resource exhaustion and OOM kills affecting other pods."
        )
    
    if efficiency.resource_coverage_percentage < 70:
        recommendations.append(
            f"📊 **Low resource coverage** ({efficiency.resource_coverage_percentage:.1f}%). "
            "Aim for 90%+ coverage to ensure cluster stability and predictable performance."
        )
    
    if efficiency.unused_config_maps > 0:
        recommendations.append(
            f"🗂️ **{efficiency.unused_config_maps} unused ConfigMaps** detected. "
            "Review and clean up unused configuration objects to reduce cluster clutter."
        )
    
    if efficiency.orphaned_pvcs > 0:
        recommendations.append(
            f"💾 **{efficiency.orphaned_pvcs} orphaned PVCs** in pending state. "
            "Check storage classes and provisioners to resolve storage issues."
        )
    
    if not recommendations:
        recommendations.append(
            "✅ **Excellent resource management!** Your cluster shows good resource governance practices. "
            "Continue monitoring to maintain this high standard."
        )
    
    for rec in recommendations:
        st.markdown(rec)
    
    # Export functionality
    st.subheader("📤 Export Resource Issues")
    
    if efficiency.problematic_pods:
        # Create export data
        export_data = {
            'summary': {
                'total_pods_analyzed': efficiency.total_pods_analyzed,
                'resource_coverage_percentage': efficiency.resource_coverage_percentage,
                'pods_without_requests': efficiency.pods_without_requests,
                'pods_without_limits': efficiency.pods_without_limits,
                'pods_without_any_resources': efficiency.pods_without_any_resources
            },
            'problematic_pods': [pod.dict() for pod in efficiency.problematic_pods],
            'recommendations': recommendations
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download Full Report (JSON)",
                data=json.dumps(export_data, indent=2, default=str),
                file_name=f"resource_efficiency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Create CSV for problematic pods
            csv_data = []
            for pod in efficiency.problematic_pods:
                csv_data.append({
                    'pod_name': pod.name,
                    'namespace': pod.namespace,
                    'severity': pod.issue_severity,
                    'missing_requests': ','.join(pod.missing_requests),
                    'missing_limits': ','.join(pod.missing_limits),
                    'health_status': pod.health_status,
                    'containers': ','.join(pod.containers),
                    'recommendations': ' | '.join(pod.recommendations)
                })
            
            if csv_data:
                csv_df = pd.DataFrame(csv_data)
                csv_string = csv_df.to_csv(index=False)
                
                st.download_button(
                    label="📊 Download CSV Report",
                    data=csv_string,
                    file_name=f"pod_resource_issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Quick fix examples
    if efficiency.problematic_pods:
        st.subheader("🔧 Quick Fix Examples")
        
        st.markdown("""
        **Add resource requests and limits to your pod specifications:**
        
        ```yaml
        apiVersion: v1
        kind: Pod
        metadata:
          name: example-pod
        spec:
          containers:
          - name: app-container
            image: nginx
            resources:
              requests:
                memory: "64Mi"
                cpu: "250m"
              limits:
                memory: "128Mi"
                cpu: "500m"
        ```
        
        **Best Practices:**
        - Set requests based on actual resource usage patterns
        - Set limits slightly higher than requests to allow bursting
        - Monitor actual usage and adjust over time
        - Use VPA (Vertical Pod Autoscaler) for automatic recommendations
        """)
