# EmergentIntelliTest Backend

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A modern, AI-powered test automation platform built with FastAPI, PostgreSQL, and Supabase. EmergentIntelliTest helps teams manage test cases, execute tests, and generate intelligent test scenarios using AI.

## ✨ Features

- **AI-Powered Test Generation**
  - Automatically generate test cases from requirements
  - Smart test step suggestions
  - Natural language processing for test creation

- **Comprehensive Test Management**
  - Hierarchical test organization
  - Version control for test cases
  - Tagging and categorization

- **Powerful Execution Engine**
  - Parallel test execution
  - Detailed execution history
  - Real-time status updates

- **Collaboration Tools**
  - Team workspaces
  - Comments and discussions
  - Role-based access control

- **Analytics & Reporting**
  - Test coverage analysis
  - Execution trends
  - Customizable dashboards

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for caching and background tasks)
- [Poetry](https://python-poetry.org/) (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/emergent-intellitest.git
   cd emergent-intellitest/backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using Poetry
   poetry install
   ```

4. **Initialize the database**
   ```bash
   python -c "from app.db.init_db import init; init()"
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

7. **Access the application**
   - API: http://localhost:8001
   - Interactive API docs: http://localhost:8001/docs
   - Alternative API docs: http://localhost:8001/redoc

## 🏗 Project Structure

```
backend/
├── app/                    # Application source code
│   ├── api/               # API routes
│   ├── core/              # Core functionality
│   ├── db/                # Database configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry point
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
└── requirements.txt       # Python dependencies
```

## 📚 Documentation

- [API Reference](docs/API_REFERENCE.md) - Comprehensive API documentation
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [Testing Strategy](tests/TESTING_STRATEGY.md) - Testing approach and guidelines

## 🛠 Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8

# Check types
mypy .
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database powered by [PostgreSQL](https://www.postgresql.org/) and [Supabase](https://supabase.com/)
- Testing with [pytest](https://docs.pytest.org/)
- Project structure inspired by [Full Stack FastAPI PostgreSQL](https://github.com/tiangolo/full-stack-fastapi-postgresql)

---

<div align="center">
  Made with ❤️ by the EmergentIntelliTest Team
</div>
