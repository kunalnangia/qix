# Deployment Guide

This document outlines the steps to deploy the IntelliTest AI Automation Platform.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Node.js 16+ (for frontend)
- Docker (optional, for containerized deployment)
- Redis (for caching and async tasks)

## Backend Setup

### 1. Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Application
PROJECT_NAME="IntelliTest AI Automation Platform"
SECRET_KEY="your-secret-key-change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=11520
SERVER_NAME="your-domain.com"
SERVER_HOST="https://your-domain.com"

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# CORS (comma-separated list of allowed origins)
BACKEND_CORS_ORIGINS='["http://localhost:3000", "https://your-frontend-domain.com"]'

# Email (optional, for notifications)
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST="smtp.example.com"
SMTP_USER="your-email@example.com"
SMTP_PASSWORD="your-email-password"

# JWT Settings
JWT_SECRET_KEY="your-jwt-secret-key"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Database Setup

1. Create a PostgreSQL database
2. Run database migrations:

```bash
alembic upgrade head
```

### 4. Run the Application

For development:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

For production with Gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8001
```

## Frontend Setup

### 1. Environment Variables

Create a `.env` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com/api/v1
NEXT_PUBLIC_APP_URL=https://your-frontend-domain.com
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

### 3. Build and Run

For development:
```bash
npm run dev
```

For production:
```bash
npm run build
npm start
```

## Docker Deployment (Optional)

### 1. Build the Docker Images

```bash
docker-compose build
```

### 2. Start the Services

```bash
docker-compose up -d
```

## Configuration Management

### Environment Variables

All sensitive configuration should be managed through environment variables. Never commit sensitive data to version control.

### Secrets Management

For production, consider using a secrets management service like:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

## Monitoring and Logging

### Backend Logs

- Logs are written to `logs/app.log`
- Log rotation is configured for production

### Error Tracking

Consider integrating with:
- Sentry
- Datadog
- New Relic

## Backup and Recovery

### Database Backups

Set up regular database backups using:
- `pg_dump` for PostgreSQL
- AWS RDS automated backups
- Custom backup scripts

### Media Files

If your application handles file uploads, ensure they are stored in a persistent volume and regularly backed up.

## Scaling

### Horizontal Scaling

- Use a load balancer (Nginx, AWS ALB)
- Configure multiple backend instances
- Use Redis for session management

### Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Consider sharding for very large datasets

## Security Considerations

1. Always use HTTPS
2. Set appropriate CORS policies
3. Implement rate limiting
4. Regularly update dependencies
5. Use security headers
6. Implement proper authentication and authorization
7. Regular security audits

## Maintenance

1. Monitor application performance
2. Regularly update dependencies
3. Review and rotate secrets
4. Monitor disk space and database growth
5. Set up alerts for critical issues
