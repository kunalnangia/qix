import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the application components
from backend.database_sqlite import Base, get_db, init_db, engine
from backend.server import app
from backend import models
from backend.auth import get_password_hash, create_access_token

# Override the database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test database setup
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test database tables
Base.metadata.create_all(bind=test_engine)

# Test client with test database
client = TestClient(app)

# Fixture to get a test database session
@pytest.fixture(scope="function")
def test_db():
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    
    # Run the test
    try:
        yield db
    finally:
        # Clean up after the test
        db.close()
        Base.metadata.drop_all(bind=test_engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

# Test data
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}

def create_test_user():
    db = next(override_get_db())
    hashed_password = get_password_hash(TEST_USER["password"])
    db_user = models.User(
        id=str(uuid.uuid4()),
        email=TEST_USER["email"],
        hashed_password=hashed_password,
        full_name=TEST_USER["full_name"],
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_auth_headers(user_id: str):
    access_token = create_access_token(data={"sub": user_id})
    return {"Authorization": f"Bearer {access_token}"}

# Fixtures
@pytest.fixture(scope="function")
def test_db():
    # Create the database and the database tables
    Base.metadata.create_all(bind=engine)
    
    # Run the tests
    yield
    
    # Clean up the database after tests
    Base.metadata.drop_all(bind=engine)

# Test cases
def test_register_user(test_db):
    # Test user registration
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User"
    }
    response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()
    assert response.json()["user"]["email"] == "newuser@example.com"

def test_login(test_db):
    # Create a test user first
    test_user = create_test_user()
    
    # Test successful login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_create_project(test_db):
    # Create a test user
    test_user = create_test_user()
    
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test project creation
    project_data = {
        "name": "Test Project",
        "description": "A test project"
    }
    response = client.post(
        "/api/v1/projects/",
        json=project_data,
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"
    assert "id" in response.json()

# Add more test cases for other endpoints

def test_create_test_case(test_db):
    # Create test user and project
    test_user = create_test_user()
    headers = get_auth_headers(test_user.id)
    
    # Create a project first
    project = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers=headers
    ).json()
    
    # Test test case creation
    test_case_data = {
        "title": "Sample Test Case",
        "description": "Test case description",
        "project_id": project["id"],
        "test_type": "functional",
        "priority": "high",
        "status": "draft",
        "steps": [
            {"step_number": 1, "action": "Open application", "expected_result": "Application opens successfully"},
            {"step_number": 2, "action": "Login with valid credentials", "expected_result": "User is logged in"}
        ]
    }
    
    response = client.post(
        "/api/v1/test-cases/",
        json=test_case_data,
        headers=headers
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Sample Test Case"
    assert len(response.json()["steps"]) == 2

def test_get_test_cases(test_db):
    # Setup test data
    test_user = create_test_user()
    headers = get_auth_headers(test_user.id)
    
    # Create a project
    project = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers=headers
    ).json()
    
    # Create test cases
    test_case_data = {
        "title": "Test Case 1",
        "project_id": project["id"],
        "test_type": "functional"
    }
    client.post("/api/v1/test-cases/", json=test_case_data, headers=headers)
    
    # Test getting test cases
    response = client.get(
        f"/api/v1/test-cases/?project_id={project['id']}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == "Test Case 1"

def test_create_test_case(test_db):
    # Create test user and get auth token
    test_user = create_test_user()
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a project first
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "Test"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # Test test case creation
    test_case_data = {
        "title": "Sample Test Case",
        "description": "Test case description",
        "project_id": project_id,
        "test_type": "functional",
        "priority": "high",
        "status": "draft",
        "steps": [
            {"step_number": 1, "action": "Open application", "expected_result": "Application opens successfully"},
            {"step_number": 2, "action": "Login with valid credentials", "expected_result": "User is logged in"}
        ]
    }
    
    response = client.post(
        "/api/v1/test-cases/",
        json=test_case_data,
        headers=headers
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Sample Test Case"
    assert len(response.json()["steps"]) == 2

def test_get_test_cases(test_db):
    # Setup test data
    test_user = create_test_user()
    
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # Create test case
    test_case_data = {
        "title": "Test Case 1",
        "project_id": project_id,
        "test_type": "functional"
    }
    client.post(
        "/api/v1/test-cases/", 
        json=test_case_data, 
        headers=headers
    )
    
    # Test getting test cases
    response = client.get(
        f"/api/v1/test-cases/?project_id={project_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["title"] == "Test Case 1"

def test_update_test_case(test_db):
    # Setup test data
    test_user = create_test_user()
    
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # Create test case
    test_case_data = {
        "title": "Test Case to Update",
        "project_id": project_id,
        "test_type": "functional"
    }
    create_response = client.post(
        "/api/v1/test-cases/", 
        json=test_case_data, 
        headers=headers
    )
    test_case_id = create_response.json()["id"]
    
    # Update test case
    update_data = {"title": "Updated Test Case"}
    response = client.put(
        f"/api/v1/test-cases/{test_case_id}",
        json=update_data,
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Case"

def test_delete_test_case(test_db):
    # Setup test data
    test_user = create_test_user()
    
    # Get auth token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a project
    project_response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # Create test case
    test_case_data = {
        "title": "Test Case to Delete",
        "project_id": project_id,
        "test_type": "functional"
    }
    create_response = client.post(
        "/api/v1/test-cases/", 
        json=test_case_data, 
        headers=headers
    )
    test_case_id = create_response.json()["id"]
    
    # Delete test case
    response = client.delete(
        f"/api/v1/test-cases/{test_case_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Test case deleted successfully"
    
    # Verify deletion
    get_response = client.get(
        f"/api/v1/test-cases/{test_case_id}",
        headers=headers
    )
    assert get_response.status_code == 404

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_core_features.py"])
