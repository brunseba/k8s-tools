# Dummy Data for Kubernetes Analysis Tools

This directory contains comprehensive sample Kubernetes YAML files designed for testing and demonstrating the capabilities of k8s-analyzer and k8s-reporter tools. The data represents realistic enterprise-grade applications with proper labeling, security configurations, and compliance requirements.

## Directory Structure

```
dummy-data/
├── cluster-exports/          # Complete cluster exports
├── manifests/               # Individual resource manifests
├── multi-cluster/          # Multi-cluster deployment examples
└── README.md               # This file
```

## Applications Overview

The dummy data includes 5 different enterprise applications across 10 namespaces:

1. **Healthcare Management System** - Patient records, appointments, HIPAA compliance
2. **E-commerce Platform** - Online shopping, catalog, orders, payments
3. **Retail Point-of-Sale** - In-store transactions, inventory, PCI DSS compliance
4. **Financial Services** - Payment processing, billing, reporting
5. **Logistics Management** - Inventory tracking, delivery management

## Kubernetes Resources by Kind

### Namespaces (10 total)
- **healthcare-frontend** - Frontend services for healthcare platform
- **healthcare-backend** - Backend APIs and services for healthcare
- **healthcare-data** - Database and data services for healthcare
- **healthcare-analytics** - Analytics and reporting for healthcare
- **healthcare-integration** - Integration services (HL7, FHIR)
- **retail-sales** - Point-of-sale and sales management
- **retail-inventory** - Inventory management and tracking
- **ecommerce-frontend** - E-commerce web interfaces
- **ecommerce-backend** - E-commerce backend services
- **finance** - Financial processing and billing

**Labels Used:**
- `application`: Groups resources by business domain
- `tier`: Technical layer (frontend, backend, database, analytics)
- `environment`: Deployment environment (production, staging, development)
- `team`: Owning team for operational responsibility
- `compliance`: Regulatory requirements (hipaa, pcidss, sox)
- `data-classification`: Data sensitivity level

### Deployments (15+ instances)
Comprehensive application deployments with:
- **Resource specifications** - CPU, memory, storage limits and requests
- **Health probes** - Liveness, readiness, and startup probes
- **Security contexts** - Non-root users, capability drops, read-only filesystems
- **Environment variables** - Configuration and secrets integration
- **Volume mounts** - Config files, SSL certificates, persistent storage
- **Affinity rules** - Pod anti-affinity for high availability
- **Tolerations** - Node selection and scheduling preferences

**Key Applications:**
- `patient-portal` - Healthcare patient interface (25 replicas)
- `patient-service` - Patient management API (20 replicas)
- `appointment-service` - Appointment scheduling (15 replicas)
- `product-catalog-api` - E-commerce catalog service (15 replicas)
- `order-management-api` - Order processing (12 replicas)
- `pos-system` - Retail point-of-sale (10 replicas)
- `inventory-service` - Inventory management (12 replicas)

### StatefulSets (4 instances)
Database and stateful services:
- **healthcare-postgresql** - Primary healthcare database (PostgreSQL 14.9)
- **retail-postgresql** - Retail application database (PostgreSQL 13.3)
- **elasticsearch-cluster** - E-commerce search engine (6 replicas)
- **redis-cluster** - Caching and session storage

**Features:**
- Volume claim templates for persistent storage
- Service discovery through headless services
- Database initialization scripts
- Monitoring exporters (Prometheus metrics)
- Replication and backup configurations

### Services (12+ instances)
Load balancing and service discovery:
- **LoadBalancer services** - External access with AWS NLB annotations
- **ClusterIP services** - Internal service communication
- **NodePort services** - Development and testing access
- **Headless services** - StatefulSet service discovery

**Service Types by Application:**
- Healthcare: Patient portal, API services, database connections
- E-commerce: Web storefront, catalog API, search services
- Retail: POS terminals, inventory APIs
- Multi-port configurations for HTTP/HTTPS, metrics, management

### ConfigMaps (8+ instances)
Application and infrastructure configuration:

#### Application Configurations
- **patient-portal-config** - Healthcare portal settings, security, features
- **patient-service-config** - Spring Boot configuration, database pools, Kafka
- **pos-system-config** - Retail POS features, security, compliance
- **inventory-service-config** - Inventory management, caching, notifications

#### Infrastructure Configurations
- **nginx.conf** - Reverse proxy, SSL termination, rate limiting, security headers
- **postgresql.conf** - Database tuning, connection pools, performance settings
- **prometheus.yml** - Monitoring configuration, scrape targets, alerting
- **elasticsearch.yml** - Search cluster configuration, security, performance

**Configuration Categories:**
- Security settings (timeouts, authentication, encryption)
- Feature flags (toggles for functionality)
- Performance tuning (connection pools, caching, timeouts)
- Compliance controls (audit logging, data retention)
- Integration endpoints (APIs, databases, message queues)

### Secrets (10+ instances)
Secure credential and certificate management:

#### Database Credentials
- **healthcare-database-credentials** - PostgreSQL connection strings, usernames, passwords
- **retail-database-credentials** - Retail database access credentials
- **elasticsearch-credentials** - Search cluster authentication

#### Application Secrets
- **healthcare-app-secrets** - JWT tokens, encryption keys, session secrets
- **retail-app-secrets** - POS system encryption, payment processing keys
- **aws-credentials** - Cloud storage and services access

#### SSL/TLS Certificates
- **healthcare-ssl-certificates** - HTTPS certificates for healthcare services
- **retail-ssl-certificates** - PCI DSS compliant certificates for retail

**Security Features:**
- Base64 encoded values with comments showing plaintext
- Separate secrets per namespace for isolation
- Multi-purpose secrets (database + application + certificates)
- Compliance-specific secrets (HIPAA, PCI DSS requirements)

### ServiceAccounts (8 instances)
RBAC and service authentication:
- **healthcare-frontend-sa** - Frontend service permissions
- **healthcare-backend-sa** - Backend API permissions  
- **healthcare-data-sa** - Database access permissions
- **retail-sales-sa** - Sales system permissions
- **retail-inventory-sa** - Inventory management permissions
- **retail-data-sa** - Retail database permissions

**Features:**
- Namespace isolation for security
- Application-specific permissions
- Compliance labeling for audit trails

### PersistentVolumeClaims (6+ instances)
Storage requirements for different use cases:

#### Healthcare Storage
- **healthcare-audit-logs-pvc** - HIPAA audit trail storage (500Gi, ReadWriteMany)
- **patient-documents-pvc** - Medical records and documents (2000Gi, ReadWriteMany)

#### E-commerce Storage
- **static-assets-pvc** - Web assets and media files
- **order-files-pvc** - Order processing documents
- **image-cache-pvc** - Product image caching

**Storage Classes:**
- `encrypted-high-performance-ssd` - High IOPS for databases
- `encrypted-standard-ssd` - General purpose encrypted storage
- `standard` - Basic persistent storage
- `fast-ssd` - Performance-optimized storage

### Jobs and CronJobs (3 instances)
Batch processing and scheduled tasks:
- **daily-report-generator** - Financial reporting (daily at 1 AM)
- **inventory-sync** - Inventory synchronization job
- **data-migration** - Database migration tasks

**Features:**
- Cron schedule expressions
- Resource limits for batch operations
- Persistent volume integration for output
- Retry and failure policies

## Compliance and Security Features

### HIPAA Compliance (Healthcare)
- Audit logging enabled for all PHI access
- Data encryption at rest and in transit
- Access controls and authentication
- Data retention policies (7 years)
- Patient data isolation and security

### PCI DSS Compliance (Retail/Finance)
- Payment card data protection
- Secure payment processing
- Network segmentation
- Regular security monitoring
- Encrypted communication channels

### Security Best Practices
- Non-root container execution
- Read-only root filesystems
- Capability dropping (ALL capabilities removed)
- Security contexts and seccomp profiles
- Network policies and service mesh integration
- Regular credential rotation

## Label Strategy

### Organizational Labels
- `application`: Business application grouping
- `team`: Owning team for operations
- `cost-center`: Financial tracking and chargeback

### Technical Labels  
- `tier`: Architecture layer classification
- `component`: Specific functional component
- `version`: Application version tracking

### Operational Labels
- `environment`: Deployment stage
- `compliance`: Regulatory requirements
- `data-classification`: Data sensitivity level

### Example Label Usage
```yaml
labels:
  application: healthcare
  tier: backend
  component: patient-management
  team: backend-team
  environment: production
  compliance: hipaa
  data-classification: sensitive
  version: v2.8.4
  cost-center: "2002"
```

## File Sizes and Resource Counts

### Large Files (40KB+)
- `healthcare-platform.yaml` - 42KB, 30+ resources
- `ecommerce-platform.yaml` - 34KB, 25+ resources

### Medium Files (10-20KB)
- `retail-platform.yaml` - 18KB, 15+ resources
- `finance-logistics-combined.yaml` - 12KB, 20+ resources

### Resource Distribution
- **Total Resources**: 100+ Kubernetes resources
- **Total Size**: 150KB+ of YAML configuration
- **Namespaces**: 10 across 5 applications
- **Deployments**: 15+ with comprehensive configurations
- **StatefulSets**: 4 database and storage systems
- **ConfigMaps**: 8+ with detailed application settings
- **Secrets**: 10+ covering all credential types

## Usage Examples

### Analyze Healthcare Resources
```bash
k8s-analyzer parse dummy-data/cluster-exports/healthcare-platform.yaml --filter="compliance=hipaa"
```

### Generate Retail Compliance Report
```bash
k8s-reporter generate --input dummy-data/cluster-exports/retail-platform.yaml --output retail-report.html --filter="compliance=pcidss"
```

### Multi-Application Analysis
```bash
k8s-analyzer batch --directory dummy-data/cluster-exports/ --export-format sqlite --output analysis.db
```

### Resource Relationship Analysis
```bash
k8s-analyzer relationships --input dummy-data/cluster-exports/ecommerce-platform.yaml --visualize --output ecommerce-graph.png
```

## Testing Scenarios

The dummy data supports various testing scenarios:

1. **Single Application Analysis** - Healthcare, e-commerce, retail platforms
2. **Multi-Namespace Operations** - Cross-namespace resource relationships
3. **Compliance Reporting** - HIPAA, PCI DSS, SOX compliance checks
4. **Resource Optimization** - CPU, memory, storage analysis
5. **Security Assessment** - Security context, RBAC, network policy analysis
6. **Label-Based Filtering** - Team, application, compliance-based queries
7. **Performance Analysis** - Resource utilization and scaling patterns
8. **Cost Analysis** - Resource allocation and cost center reporting

This comprehensive dataset provides realistic enterprise scenarios for thorough testing of Kubernetes analysis and reporting tools.
