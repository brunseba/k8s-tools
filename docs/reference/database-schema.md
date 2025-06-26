# 🛠️ Database Schema Reference

This document provides an in-depth look at the database schema utilized by k8s-analyzer and k8s-reporter to store analysis results, resource relationships, and historical data.

## Overview

The database schema is designed to efficiently store and query large volumes of Kubernetes resource data. It supports typical operations like insertions, updates, deletions, and complex queries for generating reports and conducting analyses.

## Core Tables

### `resources`
Stores metadata and analysis results for all Kubernetes resources.

```sql
CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT UNIQUE,
    name TEXT NOT NULL,
    namespace TEXT,
    kind TEXT NOT NULL,
    api_version TEXT NOT NULL,
    health_status TEXT NOT NULL,
    issues TEXT,  -- JSON array of issue descriptions
    labels TEXT,  -- JSON object of labels
    annotations TEXT,  -- JSON object of annotations
    spec TEXT,    -- JSON object of resource spec
    status TEXT,  -- JSON object of resource status
    creation_timestamp DATETIME,
    deletion_timestamp DATETIME,
    resource_version TEXT,
    generation INTEGER,
    owner_references TEXT,  -- JSON array of owner references
    finalizers TEXT,  -- JSON array of finalizers
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

- **Indexes**: 
  - `idx_resources_kind`: Index on kind
  - `idx_resources_namespace`: Index on namespace
  - `idx_resources_creation_timestamp`: Index on creation timestamp

### `relationships`
Captures relationships between resources, such as dependencies and ownerships.

```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_uid TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_namespace TEXT,
    target_uid TEXT,
    target_kind TEXT NOT NULL,
    target_name TEXT NOT NULL,
    target_namespace TEXT,
    relationship_type TEXT NOT NULL,
    direction TEXT NOT NULL DEFAULT 'outbound',
    strength REAL DEFAULT 1.0,
    metadata TEXT,  -- JSON object of relationship metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_uid) REFERENCES resources (uid)
);
```

- **Indexes**: 
  - `idx_relationships_source_uid`: Index on source UID
  - `idx_relationships_target_uid`: Index on target UID

### `resource_health_history`
Tracks and logs the changes in health status of resources over time.

```sql
CREATE TABLE resource_health_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_uid TEXT NOT NULL,
    health_status TEXT NOT NULL,
    issues TEXT,  -- JSON array of issues at this point in time
    timestamp DATETIME NOT NULL,
    analysis_run_id TEXT,  -- Optional: link to specific analysis run
    FOREIGN KEY (resource_uid) REFERENCES resources (uid)
);
```

### `analysis_summary`
Provides a high-level summary of each analysis run, including resource counts and health distributions.

```sql
CREATE TABLE analysis_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_timestamp DATETIME NOT NULL,
    analysis_duration_seconds REAL,
    total_resources INTEGER NOT NULL,
    total_relationships INTEGER NOT NULL,
    health_summary TEXT,  -- JSON object with health statistics
    resource_types TEXT,  -- JSON object with resource type counts
    namespace_summary TEXT,  -- JSON object with namespace statistics
    cluster_info TEXT,  -- JSON object with cluster metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Query Examples

### Fetch All Resources By Kind
```sql
SELECT * FROM resources WHERE kind = 'Pod';
```

### Find Critical Issues
```sql
SELECT * FROM resources WHERE health_status = 'error';
```

### Analyze Resource Relationships
```sql
SELECT * 
FROM relationships 
WHERE source_kind = 'Deployment' 
AND target_kind = 'ReplicaSet';
```

## Best Practices

- Use indexes to improve query performance.
- Regularly back up database contents to prevent data loss.
- Use transactions to manage batch updates and maintain data integrity.

## Conclusion

Understanding the database schema allows advanced users to extend k8s-tools, perform custom queries, and integrate with other systems more efficiently. Always refer to this schema when developing extended functionalities or troubleshooting database-related issues.
