# QIX - Quality Intelligence eXperience

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen)](https://nodejs.org/)
[![CI/CD](https://github.com/kunalnangia/qix/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/kunalnangia/qix/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

QIX (Quality Intelligence eXperience) is an AI-powered test automation platform that helps teams create, manage, and execute automated tests with the power of AI. The platform provides features like test case generation, visual testing, and test execution powered by AI.

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [🚀 Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

- **AI-Powered Test Generation**: Generate test cases automatically using AI
- **Visual Testing**: Compare UI changes visually across different test runs
- **Project Management**: Organize test cases into projects and test plans
- **Team Collaboration**: Share test results and collaborate with team members
- **CI/CD Integration**: GitHub Actions for automated testing and deployment
- **Comprehensive Reporting**: Get detailed reports on test execution and coverage
- **RESTful API**: Built with FastAPI for high performance and async support
- **Modern Frontend**: Responsive UI built with Next.js and React

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **AI Integration**: OpenAI API
- **Caching**: Redis
- **Async Tasks**: Celery
- **Containerization**: Docker
- **Testing**: Pytest
- **Code Quality**: Black, isort, flake8

### Frontend
- **Framework**: Next.js (React) with TypeScript
- **State Management**: React Query
- **UI Components**: Chakra UI
- **Form Handling**: React Hook Form
- **Testing**: Jest, React Testing Library

### Infrastructure
- **Version Control**: GitHub
- **CI/CD**: GitHub Actions
- **Container Orchestration**: Docker Compose
- **Monitoring**: (To be implemented)

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9 or higher
- Node.js 16.x or higher
- PostgreSQL 13+
- Redis
- Docker (optional, for containerized deployment)
- Git
- **UI Library**: Tailwind CSS + Shadcn/UI
- **State Management**: React Query
- **Form Handling**: React Hook Form
- **Data Fetching**: Axios
- **Testing**: Jest, React Testing Library

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intellitest.git
   cd intellitest
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env` in both `backend` and `frontend` directories
   - Update the variables according to your environment

5. **Run the application**
   - Start the backend:
     ```bash
     cd ../backend
     uvicorn app.main:app --reload
     ```
   - Start the frontend:
     ```bash
     cd ../frontend
     npm run dev
     ```

### Docker Setup

1. **Generate SSL certificates** (for local HTTPS)
   ```bash
   chmod +x generate-certs.sh
   ./generate-certs.sh
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: https://localhost:3000
   - Backend API: https://localhost:8000/api/v1
   - API Documentation: https://localhost:8000/docs

## 📚 Documentation

- [API Documentation](./docs/API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Testing Guide](./docs/TESTING.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com).

---

<div align="center">
  Made with ❤️ by Your Team Name
</div>