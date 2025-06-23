## Unreleased

## v0.7.3 (2025-06-23)

### 🔧 Bug Fixes
- **BREAKING**: Fixed timestamp queries to use `creation_timestamp` instead of `created_at`
  - All time-based analysis now uses actual Kubernetes resource creation time
  - Affects namespace components, storage analysis, temporal analysis, and resource efficiency
  - Provides accurate age calculations and timeline reporting
- Added missing `datetime` import to views.py
  - Fixes NameError in resource efficiency export functionality
- Fixed timezone mismatch in temporal analysis
  - Made `datetime.now()` timezone-aware using `timezone.utc`
  - Consistent handling for both timezone-aware and naive timestamps
  - Prevents TypeError when comparing different timezone formats

### 📊 Improvements
- Enhanced accuracy of all time-based metrics and reporting
- Improved export functionality reliability
- Better error handling for datetime operations

## v0.7.0 (2025-06-23)

### ⚡ New Features - Resource Efficiency Analysis
- **Pod Resource Efficiency Analysis**: Comprehensive detection of pods without resource requests and limits
- **Severity Classification**: Automatic categorization (critical, high, medium, low) based on missing resources
- **Multi-container Support**: Analysis of complex pods with multiple containers
- **Resource Coverage Metrics**: Percentage tracking of properly configured pods
- **Automated Recommendations**: Specific guidance for fixing resource configuration issues
- **Export Capabilities**: JSON and CSV export for problematic pod reports
- **Quick Fix Examples**: YAML templates and best practices documentation

### 🎯 Focus Areas
- Identification of pods without CPU/memory requests (scheduling issues)
- Detection of pods without CPU/memory limits (resource exhaustion risks)
- Analysis of pods with partial resource configurations
- Cluster stability and resource governance insights

## v0.6.0 (2025-06-23)

### 💾 New Features - Storage Analysis
- **Global Storage Consumption**: Cluster-wide storage analysis with capacity tracking
- **Per-namespace Storage Breakdown**: Detailed storage analysis by namespace
- **Storage Class Analytics**: Distribution and capacity by storage class
- **Volume Status Tracking**: Bound, available, pending, and orphaned volume detection
- **Top Storage Consumers**: Identification of largest volumes and capacity usage
- **Access Pattern Analysis**: ReadWriteOnce, ReadOnlyMany, etc. usage patterns

### ⏰ New Features - Temporal Analysis
- **Resource Lifecycle Tracking**: Creation timeline and age-based categorization
- **Temporal Patterns**: Resource creation patterns over time
- **Age Distribution**: New, recent, active, mature, and stale resource identification
- **Most Active Namespaces**: Resource creation activity tracking
- **Creation Timeline**: Detailed timeline of resource creation events
- **Lifecycle Statistics**: Average age and lifecycle metrics by resource type

### 📊 Enhanced Analytics
- Interactive charts for storage and temporal data
- Timeline visualizations for resource creation patterns
- Capacity utilization metrics and trending
- Age-based resource health insights

## v0.5.0 (2025-06-23)

### 🏗️ New Features - Namespace Components View
- **Detailed Per-namespace Analysis**: Comprehensive component view with relationships
- **Resource Relationship Mapping**: Interactive dependency visualization
- **Component Grouping**: Automatic organization by resource type
- **Dependency Chain Analysis**: Ordered dependency chain detection
- **Orphaned Component Detection**: Identification of resources without relationships
- **Critical Component Identification**: Resources with high relationship counts
- **Interactive Network Graphs**: Visual representation of component relationships using NetworkX

### 🔗 Relationship Analytics
- Source and target relationship mapping
- Relationship strength and type analysis
- Cross-namespace relationship tracking
- Dependency visualization and analysis

### 📊 Enhanced UI
- Interactive pie charts for component type distribution
- Bar charts for health status analysis
- Network graph visualization for relationships
- Component search and filtering capabilities
- Data export functionality for components and relationships

## v0.4.0 (2025-06-23)

### 🐛 Bug Fixes
- Fixed import errors and Pydantic validation issues
- Resolved module compatibility problems
- Enhanced error handling and validation

## v0.1.0 (2025-06-23)

### 🎉 Initial Release
- **Core Web Application**: Complete Streamlit-based dashboard for Kubernetes cluster analysis
- **SQLite Integration**: Database client for reading k8s-analyzer exported data
- **Multiple Analysis Views**: Overview, Security, Efficiency, Compliance, Health, Namespaces, Relationships
- **Interactive Features**: Resource filtering, search capabilities, and drill-down analysis
- **Data Models**: Comprehensive Pydantic models for type safety and validation
- **Visualization**: Plotly charts and interactive data presentation
- **Modern Architecture**: Python packaging with pyproject.toml and comprehensive test suite

### 📊 Core Analysis Capabilities
- Cluster health and resource distribution overview
- Security posture analysis with RBAC insights
- Resource efficiency and optimization opportunities
- Compliance reporting and best practices validation
- Namespace-level analysis and breakdown
- Resource relationship and dependency tracking
