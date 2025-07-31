# EmergentIntelliTest API Reference

This document provides a comprehensive reference for the EmergentIntelliTest API, including endpoints, request/response formats, and example usage.

## Table of Contents
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-1)
  - [Users](#users)
  - [Projects](#projects)
  - [Test Cases](#test-cases)
  - [Test Plans](#test-plans)
  - [Test Executions](#test-executions)
  - [Comments](#comments)
  - [Teams](#teams)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)
- [Filtering and Sorting](#filtering-and-sorting)
- [Webhooks](#webhooks)
- [Changelog](#changelog)

## Authentication

All API endpoints (except `/auth/login` and `/auth/register`) require authentication. Include the JWT token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

## Base URL

All API endpoints are prefixed with `/api/v1`.

Example: `https://api.example.com/api/v1/users`

## Endpoints

### Authentication

#### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false
  }
}
```

### Users

#### Get Current User

```http
GET /users/me
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-07-29T10:00:00Z",
  "updated_at": "2023-07-29T10:00:00Z"
}
```

### Projects

#### List Projects

```http
GET /projects
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)
- `sort`: Sort field (default: `-created_at`)
- `search`: Search term

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Project Alpha",
      "description": "First test project",
      "is_active": true,
      "created_at": "2023-07-29T10:00:00Z",
      "updated_at": "2023-07-29T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10,
  "total_pages": 1
}
```

### Test Cases

#### Create Test Case

```http
POST /test-cases
```

**Request Body:**
```json
{
  "title": "Login Functionality",
  "description": "Test the login functionality with valid credentials",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "steps": [
    {
      "step_number": 1,
      "action": "Navigate to login page",
      "expected_result": "Login page should be displayed"
    },
    {
      "step_number": 2,
      "action": "Enter valid credentials and click login",
      "expected_result": "User should be logged in and redirected to dashboard"
    }
  ],
  "tags": ["login", "authentication", "critical"]
}
```

### Test Plans

#### Create Test Plan

```http
POST /test-plans
```

**Request Body:**
```json
{
  "name": "Regression Test Suite - July 2023",
  "description": "Full regression test suite for July 2023 release",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "test_case_ids": [
    "660e8400-e29b-41d4-a716-446655441111",
    "660e8400-e29b-41d4-a716-446655442222"
  ]
}
```

### Test Executions

#### Start Test Execution

```http
POST /test-executions
```

**Request Body:**
```json
{
  "test_plan_id": "770e8400-e29b-41d4-a716-446655443333",
  "environment_id": "880e8400-e29b-41d4-a716-446655444444",
  "assigned_to_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Comments

#### Add Comment to Test Execution

```http
POST /test-executions/{execution_id}/comments
```

**Request Body:**
```json
{
  "content": "Found an issue with the login button on mobile view"
}
```

### Teams

#### Create Team

```http
POST /teams
```

**Request Body:**
```json
{
  "name": "QA Team",
  "description": "Quality Assurance Team",
  "member_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655441111"
  ]
}
```

## Error Handling

### Error Response Format

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid request format or parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

## Rate Limiting

- Default rate limit: 1000 requests per hour per IP
- Authentication endpoints: 100 requests per hour per IP
- Exceeding the limit returns a 429 status code with a `Retry-After` header

## Pagination

All list endpoints support pagination using `page` and `per_page` query parameters.

## Filtering and Sorting

Most list endpoints support filtering and sorting using query parameters:

- Filtering: `?field=value`
- Sorting: `?sort=field` (ascending) or `?sort=-field` (descending)
- Multiple filters: `?field1=value1&field2=value2`

## Webhooks

### Available Events

- `test_execution.started`
- `test_execution.completed`
- `test_execution.failed`
- `test_case.created`
- `test_case.updated`

### Webhook Payload Example

```json
{
  "event": "test_execution.completed",
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655449999",
    "status": "passed",
    "test_plan_id": "770e8400-e29b-41d4-a716-446655443333",
    "executed_by": "550e8400-e29b-41d4-a716-446655440000",
    "started_at": "2023-07-29T10:00:00Z",
    "completed_at": "2023-07-29T10:15:30Z"
  },
  "timestamp": "2023-07-29T10:15:30Z"
}
```

## Changelog

### v1.0.0 (2023-07-29)
- Initial API release
- Basic CRUD operations for all resources
- JWT authentication
- Pagination and filtering support
