# EmergentIntelliTest Deployment Guide

This document provides detailed instructions for deploying the EmergentIntelliTest application in various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Database Management](#database-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+ (for caching and background tasks)
- Node.js 16+ (for frontend assets if applicable)
- Git

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/emergent-intellitest.git
   cd emergent-intellitest/backend
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -c "from app.db.init_db import init; init()"
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access the application**
   - API: http://localhost:8001
   - Documentation: http://localhost:8001/docs

## Production Deployment

### Manual Deployment

1. **Set up the server**
   - Ubuntu 20.04/22.04 LTS recommended
   - 2+ CPU cores, 4GB+ RAM, 20GB+ disk space

2. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx
   ```

3. **Set up PostgreSQL**
   ```sql
   sudo -u postgres createuser -P intellitest
   sudo -u postgres createdb -O intellitest intellitest_prod
   ```

4. **Deploy the application**
   ```bash
   # As root
   mkdir -p /opt/emergent-intellitest
   chown -R intellitest:www-data /opt/emergent-intellitest
   
   # As application user
   git clone https://github.com/your-org/emergent-intellitest.git /opt/emergent-intellitest
   cd /opt/emergent-intellitest/backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Set up systemd service**
   ```bash
   sudo cp deploy/emergent-intellitest.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable emergent-intellitest
   sudo systemctl start emergent-intellitest
   ```

6. **Set up Nginx as reverse proxy**
   ```bash
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/emergent-intellitest
   sudo ln -s /etc/nginx/sites-available/emergent-intellitest /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Docker Deployment

1. **Build and start containers**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **Run database migrations**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web alembic upgrade head
   ```

3. **View logs**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Yes | - |
| `SECRET_KEY` | Secret key for JWT tokens | Yes | - |
| `ALGORITHM` | JWT algorithm | No | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | 1440 |
| `ENVIRONMENT` | Environment (dev, test, prod) | No | dev |
| `CORS_ORIGINS` | Allowed CORS origins | No | * |
| `REDIS_URL` | Redis connection URL | No | redis://localhost:6379 |

## Database Management

### Backups
```bash
# Dump database
pg_dump -U intellitest intellitest_prod > backup_$(date +%Y%m%d).sql

# Restore database
psql -U intellitest intellitest_prod < backup_20230729.sql
```

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Monitoring and Logging

### Log Locations
- Application logs: `/var/log/emergent-intellitest/app.log`
- Error logs: `/var/log/emergent-intellitest/error.log`
- Systemd logs: `journalctl -u emergent-intellitest -f`

### Monitoring with Prometheus and Grafana
1. Set up Prometheus and Grafana using the provided docker-compose.monitoring.yml
2. Access Grafana at http://your-server:3000
3. Import the provided dashboard from `deploy/grafana-dashboard.json`

## Scaling

### Horizontal Scaling
1. Set up a load balancer (Nginx, HAProxy, or cloud load balancer)
2. Deploy multiple application instances
3. Configure shared session storage (Redis recommended)

### Database Scaling
1. Set up read replicas for read-heavy workloads
2. Consider connection pooling with PgBouncer
3. Implement database sharding for very large datasets

## Troubleshooting

### Common Issues

**Database Connection Issues**
- Verify `DATABASE_URL` is correct
- Check if PostgreSQL is running and accessible
- Ensure the database user has proper permissions

**Application Not Starting**
- Check logs: `journalctl -u emergent-intellitest -n 50 --no-pager`
- Verify all environment variables are set
- Check for port conflicts

**Performance Issues**
- Monitor database queries with `pg_stat_statements`
- Check server resource usage
- Review application logs for slow requests

### Getting Help
For additional support, please open an issue on our [GitHub repository](https://github.com/your-org/emergent-intellitest/issues).
