# 📊 Analysis Views Overview

K8s-reporter provides multiple specialized analysis views, each designed to provide insights into different aspects of your Kubernetes cluster. This guide explains each view and how to use them effectively.

## Available Views

### 📊 Cluster Overview
**Purpose**: High-level cluster health and resource distribution

**Key Metrics**:
- Total resources and namespaces
- Health ratio percentage
- Resource type distribution
- Top namespaces by resource count
- Issues summary

**Use Cases**:
- Daily cluster health checks
- Executive dashboards
- Initial cluster assessment
- Resource planning

**Key Features**:
- Resource distribution pie charts
- Health metrics with visual indicators
- Top namespaces ranking
- Quick issue identification

### 🔒 Security Analysis
**Purpose**: Security posture assessment and RBAC analysis

**Key Metrics**:
- Service account usage patterns
- Pod security context evaluation
- Privileged container detection
- RBAC permissions analysis
- ConfigMaps and Secrets overview

**Use Cases**:
- Security audits
- Compliance reporting
- Vulnerability assessment
- RBAC optimization

**Key Features**:
- Security recommendations
- Privileged pod identification
- Service account analysis
- Configuration security assessment

### 🏷️ Namespace Analysis
**Purpose**: Detailed per-namespace resource breakdown

**Key Metrics**:
- Resource count per namespace
- Health distribution by namespace
- Resource types within namespaces
- Namespace-specific issues

**Use Cases**:
- Multi-tenant cluster management
- Team-based resource allocation
- Namespace-level troubleshooting
- Resource quota planning

**Key Features**:
- Interactive namespace selection
- Per-namespace health metrics
- Resource type distribution
- Cross-namespace comparison

### ❤️ Health Dashboard
**Purpose**: Resource health monitoring and issue tracking

**Key Metrics**:
- Health status distribution
- Resources with issues
- Health trends over time
- Issue categorization

**Use Cases**:
- Continuous monitoring
- Incident response
- Health trend analysis
- Proactive maintenance

**Key Features**:
- Real-time health monitoring
- Issue categorization and filtering
- Health trend visualization
- Detailed issue descriptions

### 🔗 Relationship Analysis
**Purpose**: Resource dependency mapping and relationship visualization

**Key Metrics**:
- Resource relationship counts
- Relationship type distribution
- Dependency chains
- Orphaned resources

**Use Cases**:
- Architecture understanding
- Impact analysis
- Dependency mapping
- Change planning

**Key Features**:
- Interactive relationship matrix
- Network graph visualization
- Relationship type filtering
- Dependency chain analysis

### ⚡ Resource Efficiency
**Purpose**: Resource optimization and efficiency analysis

**Key Metrics**:
- Pods without resource requests
- Pods without resource limits
- Resource coverage percentages
- Optimization opportunities

**Use Cases**:
- Resource optimization
- Cost management
- Performance tuning
- Capacity planning

**Key Features**:
- Severity classification
- Automated recommendations
- Resource coverage metrics
- Export capabilities for remediation

### 💾 Storage Analysis
**Purpose**: Storage consumption and capacity tracking

**Key Metrics**:
- Total storage consumption
- Storage class distribution
- Volume status tracking
- Per-namespace storage usage

**Use Cases**:
- Capacity planning
- Storage optimization
- Cost management
- Storage class analysis

**Key Features**:
- Storage consumption charts
- Capacity utilization metrics
- Storage class breakdown
- Volume status monitoring

### ⏰ Temporal Analysis
**Purpose**: Resource lifecycle and creation pattern analysis

**Key Metrics**:
- Resource age distribution
- Creation timeline patterns
- Most active namespaces
- Lifecycle statistics

**Use Cases**:
- Resource lifecycle management
- Creation pattern analysis
- Cleanup planning
- Activity monitoring

**Key Features**:
- Age-based categorization
- Timeline visualizations
- Creation pattern analysis
- Lifecycle statistics

## Navigation and Filtering

### Common Filters Available Across Views

**Namespace Filter**:
- Filter data by specific namespaces
- "All" option to view cluster-wide data
- Dynamically populated based on available data

**Resource Type Filter**:
- Focus on specific Kubernetes resource types
- Supports all detected resource kinds
- Useful for targeted analysis

**Health Status Filter**:
- Show only healthy, warning, or error resources
- Helps focus on problematic areas
- Supports multiple status selection

### View-Specific Features

Each view provides specialized filtering and interaction options:

- **Interactive Charts**: Click legends to toggle data series
- **Hover Tooltips**: Detailed information on data points
- **Export Functions**: Download filtered data as CSV
- **Search Capabilities**: Find specific resources by name
- **Drill-down Options**: Navigate from summary to detailed views

## Best Practices

### Daily Operations
1. Start with **Cluster Overview** for general health assessment
2. Use **Health Dashboard** to identify immediate issues
3. Check **Resource Efficiency** for optimization opportunities
4. Review **Security Analysis** for compliance monitoring

### Incident Response
1. **Health Dashboard** - Identify resources with issues
2. **Namespace Analysis** - Scope the impact to specific namespaces
3. **Relationship Analysis** - Understand dependency impacts
4. **Temporal Analysis** - Check recent changes

### Capacity Planning
1. **Storage Analysis** - Monitor storage consumption trends
2. **Resource Efficiency** - Identify optimization opportunities
3. **Namespace Analysis** - Plan resource allocation
4. **Cluster Overview** - Assess overall growth patterns

### Security Audits
1. **Security Analysis** - Comprehensive security assessment
2. **Namespace Analysis** - Per-tenant security review
3. **Relationship Analysis** - Understand access patterns
4. **Resource Efficiency** - Identify security-relevant misconfigurations

## Data Export and Integration

### Export Options
Each view supports data export functionality:
- **CSV Export**: Raw data for external analysis
- **Report Generation**: Formatted reports for stakeholders
- **API Integration**: Programmatic access to data

### Integration Patterns
```bash
# Automated report generation
k8s-reporter --database cluster.db --headless --export-reports

# Custom dashboard integration
k8s-reporter --database cluster.db --api-mode
```

## Customization

### View Configuration
Views can be customized through:
- Filter presets for common use cases
- Custom metric thresholds
- Personalized dashboard layouts
- Scheduled report generation

### Adding Custom Views
Developers can extend the analysis capabilities by:
1. Creating new view modules
2. Implementing custom analysis functions
3. Adding specialized visualizations
4. Integrating with external data sources

## Performance Considerations

### Large Clusters
- Use namespace filtering to reduce data volume
- Implement pagination for large result sets
- Cache expensive computations
- Use efficient database queries

### Real-time Monitoring
- Implement data refresh mechanisms
- Use efficient update strategies
- Monitor memory and CPU usage
- Optimize rendering performance

## Troubleshooting

### Common Issues

**Slow Loading**:
- Check database size and query complexity
- Use filters to reduce data volume
- Verify system resources

**Missing Data**:
- Verify database integrity
- Check k8s-analyzer export completeness
- Validate filter settings

**Visualization Issues**:
- Check browser compatibility
- Verify JavaScript enablement
- Test with different browsers

## Future Enhancements

### Planned Features
- **Custom Dashboard Builder**: User-defined views
- **Advanced Analytics**: Machine learning insights
- **Real-time Monitoring**: Live cluster connection
- **Multi-cluster Views**: Comparative analysis
- **Alert Integration**: Notification systems

### Community Contributions
- Custom view templates
- Specialized analysis functions
- Industry-specific dashboards
- Integration plugins

## Support and Resources

- **Documentation**: Comprehensive guides for each view
- **Examples**: Sample dashboards and use cases
- **Community**: User discussions and best practices
- **Development**: Contribution guidelines and API reference
