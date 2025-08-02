# EmergentIntelliTest - Quick Start Guide

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+** - [Download here](https://python.org/downloads)
2. **PostgreSQL 13+** - [Installation guide](https://postgresql.org/download)
3. **Redis 6.0+** - [Installation guide](https://redis.io/download)
4. **Git** - [Download here](https://git-scm.com/downloads)
5. **Poetry** (recommended) - [Installation guide](https://python-poetry.org/docs/)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kunalnangia/qix.git
cd qix/backend
```

### 2. Automated Setup (Recommended)

Run the setup script to configure everything automatically:

```bash
python setup.py
```

### 3. Manual Setup

#### Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

#### Install Dependencies

Using Poetry (recommended):
```bash
poetry install
```

Or using pip:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/intellitest

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=http://localhost:3000
```

#### Initialize Database

```bash
# Create PostgreSQL database (if not exists)
createdb intellitest

# Run database migrations
alembic upgrade head
```

#### Start the Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8001`

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
```

#### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Update database credentials, secret keys, etc.
```

#### 5. Start the Application
```bash
python main.py
```

### 🔧 Configuration

#### Database Configuration (.env)
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=intellitest
POSTGRES_PORT=5432
```

#### Security Configuration (.env)
```env
SECRET_KEY=your-super-secret-key-here
SECURITY_PASSWORD_SALT=your-password-salt-here
```

### 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8001/api/v1/docs
- **ReDoc**: http://localhost:8001/api/v1/redoc
- **Health Check**: http://localhost:8001/api/health

### 🐛 Troubleshooting

#### Common Issues

1. **Module Not Found Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify database exists: `createdb intellitest`

3. **Port Already in Use**
   ```bash
   # Kill process on port 8001
   lsof -ti:8001 | xargs kill -9
   ```

4. **Migration Issues**
   ```bash
   # Reset migrations
   alembic downgrade base
   alembic upgrade head
   ```

#### Dependency Issues Fix
```bash
# If you get import errors, try:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall
```

### 🔄 Development Workflow

1. **Start Development Server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

3. **Database Migrations**
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "Your migration message"
   
   # Apply migrations
   alembic upgrade head
   ```

### 📁 Project Structure
```
EmergentIntelliTest-main/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── alembic.ini            # Database migration config
├── setup.py               # Automated setup script
├── database/
│   ├── __init__.py        # Database package
│   ├── session.py         # Database session management
│   ├── db_models.py       # SQLAlchemy models
│   └── config.py          # Application configuration
├── uploads/               # File upload directory
└── alembic/              # Database migrations
    └── versions/         # Migration files
```

### ✅ Verification

Test your setup:
```bash
# Check if server starts
python main.py

# Check API endpoints
curl http://localhost:8001/api/health
curl http://localhost:8001/api/v1/status
```

### 🆘 Need Help?

If you encounter issues:
1. Check the logs for detailed error messages
2. Ensure all prerequisites are installed
3. Verify database connection
4. Check that all environment variables are set correctly

Happy testing! 🎉
