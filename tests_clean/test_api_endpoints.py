"""Comprehensive test for FastAPI application endpoints."""
import sys
import os
import json
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import FastAPI and create a test client
from fastapi.testclient import TestClient
from backend.server import app

# Create a test client
client = TestClient(app)

def print_test_header(test_name):
    """Print a test header for better readability."""
    print(f"\n{'='*50}")
    print(f"TEST: {test_name}")
    print(f"{'='*50}")

def test_health_check():
    """Test the health check endpoint."""
    print_test_header("Health Check Endpoint")
    response = client.get("/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✓ Health check passed")

def test_register_user():
    """Test user registration endpoint."""
    print_test_header("User Registration")
    
    # Test data
    user_data = {
        "email": f"test_{int(datetime.now().timestamp())}@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    # Make the request
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # Print and verify response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check response
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()
    assert response.json()["user"]["email"] == user_data["email"]
    
    print("✓ User registration successful")
    
    # Return the user data and token for use in other tests
    return response.json()

def test_login_user():
    """Test user login endpoint."""
    print_test_header("User Login")
    
    # First register a test user
    user_data = {
        "email": f"login_test_{int(datetime.now().timestamp())}@example.com",
        "password": "testpassword123",
        "full_name": "Login Test User"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Test login with correct credentials
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    
    # Print and verify response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check response
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()
    
    print("✓ User login successful")
    
    # Return the token for use in other tests
    return response.json()["access_token"]

def test_protected_endpoint():
    """Test accessing a protected endpoint with JWT token."""
    print_test_header("Protected Endpoint Access")
    
    # First get a valid token
    token = test_login_user()
    
    # Set up headers with the token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Access a protected endpoint
    response = client.get("/api/v1/me", headers=headers)
    
    # Print and verify response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check response
    assert response.status_code == 200
    assert "email" in response.json()
    
    print("✓ Successfully accessed protected endpoint")

def test_project_crud():
    """Test CRUD operations for projects."""
    print_test_header("Project CRUD Operations")
    
    # First get a valid token
    token = test_login_user()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a project
    project_data = {
        "name": f"Test Project {int(datetime.now().timestamp())}",
        "description": "A test project"
    }
    
    # Test create
    response = client.post("/api/v1/projects", json=project_data, headers=headers)
    print(f"Create project status: {response.status_code}")
    assert response.status_code == 200
    project = response.json()
    project_id = project["id"]
    print(f"Created project ID: {project_id}")
    
    # Test get all projects
    response = client.get("/api/v1/projects", headers=headers)
    print(f"Get all projects status: {response.status_code}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test get single project
    response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    print(f"Get project status: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id
    
    print("✓ Project CRUD operations successful")

if __name__ == "__main__":
    print("Starting comprehensive API endpoint tests...")
    
    # Run tests
    test_health_check()
    test_register_user()
    test_login_user()
    test_protected_endpoint()
    test_project_crud()
    
    print("\nAll tests completed successfully!")
