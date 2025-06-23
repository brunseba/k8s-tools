"""
Analysis views for k8s-reporter.

This module contains different view implementations for various analysis perspectives.
"""

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
