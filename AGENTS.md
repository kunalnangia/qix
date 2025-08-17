<general_rules>
When contributing to this repository, adhere to the following guidelines:

*   **Code Formatting**: Maintain consistent code style by using `black` for Python code and `isort` for sorting imports in Python.
    *   To format your Python code: `black .`
    *   To sort Python imports: `isort .`
*   **Linting**: Ensure code quality by running linters.
    *   For Python code: `flake8`
    *   For Python type checking: `mypy .`
*   **Frontend Linting**: For the frontend, use `eslint`.
    *   To run eslint: `npm run lint`
*   **Searching for existing functions/modules**: Before creating new functionalities, always search the relevant directories (e.g., `backend/app/api/`, `backend/app/services/`, `frontend/src/components/`, `frontend/src/hooks/`) to see if similar functions or modules already exist. If so, extend or reuse them; otherwise, create new ones in appropriate existing or new files.
</general_rules>

<repository_structure>
This repository is structured as a monorepo, primarily composed of a `backend` service (FastAPI) and a `frontend` application (React, Vite, TypeScript). It also includes configurations for Dockerized deployment.

*   **Root Directory**: Contains general project files, Docker Compose configuration (`docker-compose.yml`), and shared scripts.
*   **`backend/`**:
    *   `app/`: Core application source code.
        *   `api/`: Defines API routes and endpoints.
        *   `core/`: Contains core functionalities and business logic.
        *   `db/`: Manages database configurations and connections.
        *   `models/`: Defines database ORM models.
        *   `schemas/`: Contains Pydantic models for data validation and serialization.
        *   `services/`: Implements business logic and interacts with models/DB.
        *   `utils/`: Houses utility functions.
        *   `main.py`: The main entry point for the FastAPI application.
    *   `tests/`: Comprehensive test suite for the backend.
    *   `alembic/`: Manages database migrations.
    *   `scripts/`: Contains various utility scripts.
    *   `requirements.txt`: Lists Python dependencies for the backend.
*   **`frontend/`**:
    *   `src/`: Contains the React application's source code, including components, pages, and hooks.
    *   `public/`: Static assets.
    *   `package.json`: Manages Node.js dependencies for the frontend.
    *   `vite.config.ts`, `tsconfig.json`, `tailwind.config.ts`: Configuration files for Vite, TypeScript, and Tailwind CSS.
*   **`nginx/`**: Contains Nginx configuration for reverse proxying and serving both backend and frontend.
*   **`docs/`**: Holds additional documentation like API reference and deployment guides.
</repository_structure>

<dependencies_and_installation>
This project requires Docker, Docker Compose, Python, Node.js, PostgreSQL, and Redis.

**Prerequisites**:
*   Docker and Docker Compose
*   Python 3.9+
*   Node.js 16+
*   PostgreSQL 12+
*   Redis 6+

**Development Setup**:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/intellitest.git
    cd intellitest
    ```
2.  **Set up the backend**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Set up the frontend**:
    ```bash
    cd ../frontend
    npm install
    ```
4.  **Environment Variables**:
    *   Copy `.env.example` to `.env` in both `backend` and `frontend` directories.
    *   Update the variables in `.env` files according to your local environment.

5.  **Run the application**:
    *   Start the backend:
        ```bash
        cd ../backend
        uvicorn app.main:app --reload
        ```
    *   Start the frontend:
        ```bash
        cd ../frontend
        npm run dev
        ```

**Docker Setup**:

1.  **Generate SSL certificates** (for local HTTPS):
    ```bash
    chmod +x generate-certs.sh
    ./generate-certs.sh
    ```
2.  **Start the application**:
    ```bash
    docker-compose up --build
    ```
</dependencies_and_installation>

<testing_instructions>
The repository follows a testing pyramid approach, with comprehensive unit, integration, API, and E2E tests.

**Testing Frameworks**:
*   **Backend**: `pytest` is the primary testing framework. `unittest.mock` is used for mocking. `httpx` and `pytest-httpx` are used for API testing. `playwright` and `pytest-playwright` are used for E2E tests. `locust` and `k6` are used for performance testing.
*   **Frontend**: `vitest` is used for testing. `@testing-library/jest-dom`, `@testing-library/react`, and `@testing-library/user-event` are used for React component testing.

**Test Organization**:
Backend tests are organized into specific directories under `backend/tests/`:
*   `unit/`: Unit tests for individual functions and methods.
*   `integration/`: Tests for interactions between components.
*   `api/`: Tests for API endpoints (HTTP requests/responses).
*   `e2e/`: End-to-End tests for complete user flows.
*   `performance/`: Performance tests.
