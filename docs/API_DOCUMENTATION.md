# IntelliTest AI Automation Platform - API Documentation

## Base URL
All API endpoints are prefixed with `/api/v1`.

## Authentication
All endpoints require authentication using a Bearer token. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

## Projects

### Get All Projects

- **URL**: `/projects`
- **Method**: `GET`
- **Query Parameters**:
  - `skip` (optional): Number of records to skip (pagination)
  - `limit` (optional): Maximum number of records to return (default: 100, max: 100)

**Response (200 OK)**
```json
[
  {
    "id": "project-uuid",
    "name": "Project Name",
    "description": "Project Description",
    "team_id": "team-uuid-or-null",
    "created_by": "user-uuid",
    "is_active": true,
    "created_at": "2025-07-26T10:00:00Z",
    "updated_at": "2025-07-26T10:00:00Z",
    "test_case_count": 5,
    "environment_count": 2,
    "last_execution": "2025-07-26T10:30:00Z"
  }
]
```

### Get Project by ID

- **URL**: `/projects/{project_id}`
- **Method**: `GET`
- **URL Parameters**:
  - `project_id` (required): The ID of the project to retrieve

**Response (200 OK)**
```json
{
  "id": "project-uuid",
  "name": "Project Name",
  "description": "Project Description",
  "team_id": "team-uuid-or-null",
  "created_by": "user-uuid",
  "is_active": true,
  "created_at": "2025-07-26T10:00:00Z",
  "updated_at": "2025-07-26T10:00:00Z",
  "test_case_count": 5,
  "environment_count": 2,
  "last_execution": "2025-07-26T10:30:00Z"
}
```

### Create Project

- **URL**: `/projects`
- **Method**: `POST`
- **Request Body**:
  - `name` (required): Name of the project (1-200 characters)
  - `description` (optional): Project description (max 1000 characters)
  - `team_id` (optional): ID of the team this project belongs to
  - `is_active` (optional, default: true): Whether the project is active

**Request Example**
```json
{
  "name": "New Project",
  "description": "A new test project",
  "team_id": "team-uuid",
  "is_active": true
}
```

**Response (201 Created)**
```json
{
  "id": "new-project-uuid",
  "name": "New Project",
  "description": "A new test project",
  "team_id": "team-uuid",
  "created_by": "user-uuid",
  "is_active": true,
  "created_at": "2025-07-26T11:00:00Z",
  "updated_at": "2025-07-26T11:00:00Z"
}
```

### Update Project

- **URL**: `/projects/{project_id}`
- **Method**: `PUT`
- **URL Parameters**:
  - `project_id` (required): The ID of the project to update
- **Request Body**:
  - `name` (optional): New name for the project
  - `description` (optional): New description
  - `team_id` (optional): New team ID (or null to remove from team)
  - `is_active` (optional): New active status

**Request Example**
```json
{
  "name": "Updated Project Name",
  "is_active": false
}
```

**Response (200 OK)**
```json
{
  "id": "project-uuid",
  "name": "Updated Project Name",
  "description": "Project Description",
  "team_id": "team-uuid",
  "created_by": "user-uuid",
  "is_active": false,
  "created_at": "2025-07-26T10:00:00Z",
  "updated_at": "2025-07-26T12:00:00Z"
}
```

### Delete Project

- **URL**: `/projects/{project_id}`
- **Method**: `DELETE`
- **URL Parameters**:
  - `project_id` (required): The ID of the project to delete

**Response (204 No Content)**
```
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Project not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
