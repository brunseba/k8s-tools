# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.9] - 2025-06-26

### ✨ Added

**Label-based Analysis Features**
- **New Label Analysis View**: Comprehensive analysis of resource labeling patterns with coverage metrics and quality scoring
- **Enhanced Application View**: Detailed label-based resource grouping and application identification using standard Kubernetes labels
- **Orphaned Resource Detection**: Identify resources without proper application labels with actionable recommendations
- **Multi-label Analysis**: Statistical insights into label usage patterns and resource relationships
- **Interactive Label Filtering**: Search and filter resources by specific labels and applications

**Export and Reporting**
- **Application Report Export**: Download comprehensive application analysis data in JSON format
- **Label Governance Reports**: Export labeling recommendations and coverage analysis
- **Enhanced UI Elements**: Tabbed interfaces, interactive charts, and improved user experience

### 🐛 Fixed
- **Plotly Rendering Issue**: Fixed `AttributeError: 'Figure' object has no attribute 'update_xaxis'` by correcting method name to `update_xaxes`
- **Chart Display**: Resolved visualization errors in Application View charts

### 🔧 Technical Improvements
- **New Data Models**: Added `LabelAnalysis` and `ApplicationViewpoint` models for structured label analysis
- **Database Extensions**: Added 15+ new label-specific query methods to the database client
- **Comprehensive Testing**: Added 276 lines of test coverage for new label-based features
- **Enhanced UI Components**: Improved chart visualizations and interactive elements

### 📚 Documentation
- **Enhanced README**: Updated with comprehensive information about new label-based features
- **Usage Examples**: Added detailed examples for label analysis and application governance workflows
- **Best Practices**: Included Kubernetes labeling recommendations and governance guidelines

## [1.1.0] - 2025-06-25

### ✨ Added

**Comprehensive Documentation Suite**
- **MkDocs Integration**: Complete documentation website with Mermaid diagram support
- **Analysis Views Documentation**: Detailed guides for all dashboard views
- **CLI Reference**: Complete command-line interface documentation
- **Data Models**: Entity-relationship diagrams and data model documentation
- **Configuration Guides**: Comprehensive setup and configuration instructions
- **Examples and Tutorials**: Real-world usage examples and step-by-step guides
- **Troubleshooting Guide**: Common issues and solutions
- **FAQ Section**: Frequently asked questions and answers
- **Database Schema Reference**: Complete SQLite schema documentation

**Development Resources**
- **Setup Guide**: Development environment configuration
- **Contributing Guidelines**: Code standards and contribution process
- **API Reference**: Detailed API documentation

### 🔧 Technical Improvements
- **Mermaid Diagrams**: Interactive diagrams for architecture and data models
- **Searchable Documentation**: Full-text search across all documentation
- **Mobile-Friendly**: Responsive documentation design

## [0.7.3] - 2025-06-24

### ✨ Added
- **Enhanced Analysis Views**: Improved dashboard visualizations and user interface
- **Performance Optimizations**: Faster data loading and chart rendering
- **Bug Fixes**: Various stability improvements and error handling

### 🔧 Improvements
- **Database Query Optimization**: More efficient SQLite queries for large datasets
- **Memory Usage**: Reduced memory footprint for better performance
- **Error Handling**: Improved error messages and graceful failure handling

## [0.4.0] - 2025-06-20

### ✨ Added
- **Storage Analysis View**: Comprehensive storage consumption and volume analysis
- **Temporal Analysis**: Resource lifecycle tracking and age-based categorization
- **Resource Efficiency**: Pod resource optimization analysis and recommendations
- **Relationship Mapping**: Advanced resource dependency visualization

### 🔧 Improvements
- **Enhanced Visualizations**: Improved charts and interactive elements
- **Export Capabilities**: Multiple export formats for analysis data
- **Performance**: Optimized for larger clusters and datasets

## [0.1.0] - 2025-06-15

### ✨ Added
- **Initial Release**: Basic k8s-reporter functionality
- **Core Analysis Views**: Overview, Security, Namespace, and Health dashboards
- **SQLite Integration**: Database support for k8s-analyzer data
- **Web Interface**: Streamlit-based interactive dashboard
- **Basic Filtering**: Namespace and resource type filtering

### 🏗️ Infrastructure
- **Project Structure**: Initial codebase and architecture
- **Dependencies**: Core library requirements and setup
- **CLI Interface**: Basic command-line interface for launching the dashboard

---

## Upcoming Features

### 🚀 In Development
- **Environment View**: Environment-based resource grouping and analysis
- **Team Ownership**: Team-based resource ownership and governance
- **Cost Optimization**: Resource cost analysis and optimization recommendations
- **Real-time Monitoring**: Live cluster connection and real-time updates
- **Multi-cluster Support**: Compare and analyze multiple clusters

### 🎯 Planned Features
- **Custom Dashboards**: User-defined dashboard creation and customization
- **Advanced Analytics**: Machine learning insights and predictive analysis
- **Integration APIs**: REST API for external tool integration
- **Alert System**: Configurable alerts for resource issues and thresholds
- **PDF Reports**: Automated report generation and distribution

---

For more details about specific changes, see the [GitHub Releases](https://github.com/brunseba/k8s-tools/releases) page.
