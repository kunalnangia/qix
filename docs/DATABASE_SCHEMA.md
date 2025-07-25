# Database Schema Documentation

## Overview
This document provides detailed documentation of the database schema for the EmergentIntelliTest application. The database is designed to support test case management, execution, and analysis with support for both manual and AI-generated test cases.

## Table of Contents
1. [Tables](#tables)
2. [Relationships](#relationships)
3. [Enumerated Types](#enumerated-types)
4. [Indexes](#indexes)
5. [Sample Queries](#sample-queries)
6. [Best Practices](#best-practices)

## Tables

### profiles
Stores user account information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| email | text | NOT NULL | User's email address |
| full_name | text | NULL | User's full name |
| avatar_url | text | NULL | URL to user's avatar |
| role | user_role | NULL | User role (admin, manager, tester, viewer) |
| team_id | uuid | NULL | Reference to teams table |
| created_at | timestamptz | NULL | Record creation timestamp |
| updated_at | timestamptz | NULL | Record last update timestamp |

### teams
Stores team information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| name | text | NOT NULL | Team name |
| description | text | NULL | Team description |
| created_by | uuid | NULL | Reference to profiles table |
| created_at | timestamptz | NULL | Record creation timestamp |
| updated_at | timestamptz | NULL | Record last update timestamp |

### projects
Stores project information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| name | text | NOT NULL | Project name |
| description | text | NULL | Project description |
| base_url | text | NULL | Base URL for the project |
| team_id | uuid | NULL | Reference to teams table |
| created_by | uuid | NULL | Reference to profiles table |
| status | test_status | NULL | Project status (active, inactive, archived) |
| created_at | timestamptz | NULL | Record creation timestamp |
| updated_at | timestamptz | NULL | Record last update timestamp |

### test_cases
Stores test case definitions.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| title | text | NOT NULL | Test case title |
| description | text | NULL | Test case description |
| project_id | uuid | NULL | Reference to projects table |
| test_type | test_type | NULL | Type of test (functional, api, ui, etc.) |
| priority | priority_level | NULL | Test priority (low, medium, high, critical) |
| status | test_status | NULL | Test status (draft, ready, etc.) |
| steps | jsonb | NULL | Test steps in JSON format |
| expected_result | text | NULL | Expected test result |
| actual_result | text | NULL | Actual test result |
| created_by | uuid | NULL | Reference to profiles table |
| assigned_to | uuid | NULL | Reference to profiles table |
| tags | text[] | NULL | Array of tags |
| ai_generated | boolean | NULL | Whether test was AI-generated |
| self_healing_enabled | boolean | NULL | Whether self-healing is enabled |
| created_at | timestamptz | NULL | Record creation timestamp |
| updated_at | timestamptz | NULL | Record last update timestamp |

### test_executions
Tracks test execution history.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| test_case_id | uuid | NULL | Reference to test_cases table |
| status | execution_status | NULL | Execution status |
| started_at | timestamptz | NULL | When execution started |
| completed_at | timestamptz | NULL | When execution completed |
| duration_ms | integer | NULL | Execution duration in milliseconds |
| error_message | text | NULL | Error message if execution failed |
| screenshots | text[] | NULL | Array of screenshot paths |
| logs | jsonb | NULL | Execution logs |
| executed_by | uuid | NULL | Reference to profiles table |
| created_at | timestamptz | NULL | Record creation timestamp |

### api_test_configs
Stores API test configurations.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| test_case_id | uuid | NULL | Reference to test_cases table |
| method | text | NOT NULL | HTTP method (GET, POST, etc.) |
| endpoint | text | NOT NULL | API endpoint |
| headers | jsonb | NULL | Request headers |
| body | jsonb | NULL | Request body |
| expected_status | integer | NULL | Expected HTTP status code |
| expected_response | jsonb | NULL | Expected response body |
| created_at | timestamptz | NULL | Record creation timestamp |

### performance_metrics
Stores performance test results.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| execution_id | uuid | NULL | Reference to test_executions table |
| page_load_time | integer | NULL | Page load time in ms |
| first_contentful_paint | integer | NULL | FCP in ms |
| largest_contentful_paint | integer | NULL | LCP in ms |
| time_to_interactive | integer | NULL | TTI in ms |
| cumulative_layout_shift | numeric | NULL | CLS score |
| memory_usage | integer | NULL | Memory usage in bytes |
| cpu_usage | numeric | NULL | CPU usage percentage |
| network_requests | integer | NULL | Number of network requests |
| created_at | timestamptz | NULL | Record creation timestamp |

### security_scan_results
Stores security scan results.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| test_case_id | uuid | NULL | Reference to test_cases table |
| vulnerability_type | text | NULL | Type of vulnerability |
| severity | severity_level | NULL | Severity level (low, medium, high, critical) |
| description | text | NULL | Vulnerability description |
| location | text | NULL | Where the vulnerability was found |
| remediation | text | NULL | How to fix the vulnerability |
| status | text | NULL | Status (open, in_progress, resolved, false_positive) |
| created_at | timestamptz | NULL | Record creation timestamp |

### ai_test_generation_requests
Tracks AI test generation requests.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | uuid | NOT NULL | Primary key |
| project_id | uuid | NULL | Reference to projects table |
| user_input | text | NOT NULL | User's input for test generation |
| generated_tests | jsonb | NULL | Generated tests in JSON format |
| status | text | NULL | Request status |
| created_by | uuid | NULL | Reference to profiles table |
| created_at | timestamptz | NULL | Record creation timestamp |

## Relationships

- **profiles** → **teams** (many-to-one): Users belong to teams
- **teams** → **projects** (one-to-many): Teams can have multiple projects
- **projects** → **test_cases** (one-to-many): Projects contain multiple test cases
- **test_cases** → **test_executions** (one-to-many): Test cases can be executed multiple times
- **test_cases** → **api_test_configs** (one-to-one): Test cases can have API configurations
- **test_executions** → **performance_metrics** (one-to-one): Test executions can have performance metrics
- **test_cases** → **security_scan_results** (one-to-many): Test cases can have multiple security findings
- **profiles** → **ai_test_generation_requests** (one-to-many): Users can make multiple AI test generation requests

## Enumerated Types

### user_role
- admin
- manager
- tester
- viewer

### test_type
- functional
- api
- ui
- performance
- security

### priority_level
- low
- medium
- high
- critical

### test_status
- draft
- ready
- in_review
- approved
- deprecated

### execution_status
- pending
- in_progress
- passed
- failed
- blocked
- skipped

### severity_level
- low
- medium
- high
- critical

## Indexes

Primary keys are automatically indexed. The following additional indexes are recommended:

```sql
-- Example indexes for common query patterns
CREATE INDEX idx_test_cases_project_id ON test_cases(project_id);
CREATE INDEX idx_test_executions_test_case_id ON test_executions(test_case_id);
CREATE INDEX idx_test_executions_status ON test_executions(status);
CREATE INDEX idx_security_scan_results_severity ON security_scan_results(severity);
```

## Sample Queries

### Get all test cases for a project
```sql
SELECT tc.*, p.name as project_name
FROM test_cases tc
JOIN projects p ON tc.project_id = p.id
WHERE p.id = 'project-uuid';
```

### Get test execution history with performance metrics
```sql
SELECT te.*, tc.title as test_case_title, pm.*
FROM test_executions te
JOIN test_cases tc ON te.test_case_id = tc.id
LEFT JOIN performance_metrics pm ON pm.execution_id = te.id
WHERE te.test_case_id = 'test-case-uuid'
ORDER BY te.started_at DESC;
```

### Get open security issues by severity
```sql
SELECT ssr.*, tc.title as test_case_title
FROM security_scan_results ssr
JOIN test_cases tc ON ssr.test_case_id = tc.id
WHERE ssr.status = 'open'
ORDER BY 
  CASE ssr.severity
    WHEN 'critical' THEN 1
    WHEN 'high' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'low' THEN 4
  END;
```

## Best Practices

1. **Data Consistency**:
   - Always use transactions for multiple related operations
   - Use foreign key constraints to maintain referential integrity
   - Set appropriate NOT NULL constraints

2. **Performance**:
   - Add indexes for frequently queried columns
   - Use pagination for large result sets
   - Consider partitioning for large tables (e.g., test_executions)

3. **Security**:
   - Use parameterized queries to prevent SQL injection
   - Implement row-level security (RLS) for multi-tenant data
   - Encrypt sensitive data at rest

4. **Maintenance**:
   - Document all custom functions and stored procedures
   - Set up regular database backups
   - Monitor and optimize query performance regularly
