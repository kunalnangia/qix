import pytest
import httpx
import os
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8001/api"
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "test1234")

# Test client
@pytest.fixture(scope="module")
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client

# Authentication token
@pytest.fixture(scope="module")
async def auth_token(client):
    # First try to login
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = await client.post("/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try to register
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User"
    }
    response = await client.post("/auth/register", json=register_data)
    assert response.status_code == 200, "Failed to register test user"
    return response.json()["access_token"]

# Authenticated client
@pytest.fixture(scope="module")
async def auth_client(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        yield client

# Test authentication
@pytest.mark.asyncio
async def test_auth_flow(client, auth_token):
    assert auth_token is not None
    
    # Test getting current user info
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == TEST_EMAIL

# Test projects endpoints
@pytest.mark.asyncio
async def test_projects_crud(auth_client):
    # Create a test project
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    response = await auth_client.post("/projects", json=project_data)
    assert response.status_code == 200
    project = response.json()
    project_id = project["id"]
    
    # Get the project
    response = await auth_client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    
    # Update the project
    update_data = {"name": "Updated Project Name"}
    response = await auth_client.put(f"/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    
    # Get all projects
    response = await auth_client.get("/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) > 0
    
    # Delete the project
    response = await auth_client.delete(f"/projects/{project_id}")
    assert response.status_code == 200

# Test test cases endpoints
@pytest.mark.asyncio
async def test_test_cases_crud(auth_client):
    # First create a project
    project_data = {"name": "Test Project for Test Cases"}
    response = await auth_client.post("/projects", json=project_data)
    assert response.status_code == 200
    project_id = response.json()["id"]
    
    # Create a test case
    test_case_data = {
        "title": "Test Case 1",
        "description": "Test Description",
        "project_id": project_id,
        "test_type": "functional",
        "priority": "high",
        "status": "draft"
    }
    response = await auth_client.post("/test-cases", json=test_case_data)
    assert response.status_code == 200
    test_case = response.json()
    test_case_id = test_case["id"]
    
    # Get the test case
    response = await auth_client.get(f"/test-cases/{test_case_id}")
    assert response.status_code == 200
    
    # Update the test case
    update_data = {"title": "Updated Test Case Title"}
    response = await auth_client.put(f"/test-cases/{test_case_id}", json=update_data)
    assert response.status_code == 200
    
    # Get test cases by project
    response = await auth_client.get(f"/test-cases?project_id={project_id}")
    assert response.status_code == 200
    test_cases = response.json()
    assert len(test_cases) > 0
    
    # Clean up
    await auth_client.delete(f"/test-cases/{test_case_id}")
    await auth_client.delete(f"/projects/{project_id}")

# Test comments endpoints
@pytest.mark.asyncio
async def test_comments_crud(auth_client):
    # Create a project and test case first
    project_data = {"name": "Test Project for Comments"}
    response = await auth_client.post("/projects", json=project_data)
    assert response.status_code == 200
    project_id = response.json()["id"]
    
    test_case_data = {
        "title": "Test Case for Comments",
        "project_id": project_id,
        "test_type": "functional",
        "priority": "medium"
    }
    response = await auth_client.post("/test-cases", json=test_case_data)
    assert response.status_code == 200
    test_case_id = response.json()["id"]
    
    # Create a comment
    comment_data = {
        "content": "This is a test comment",
        "test_case_id": test_case_id
    }
    response = await auth_client.post("/comments", json=comment_data)
    assert response.status_code == 200
    comment = response.json()
    comment_id = comment["id"]
    
    # Get comments for test case
    response = await auth_client.get(f"/comments?test_case_id={test_case_id}")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) > 0
    
    # Mark comment as resolved
    response = await auth_client.put(f"/comments/{comment_id}/resolve")
    assert response.status_code == 200
    
    # Clean up
    await auth_client.delete(f"/test-cases/{test_case_id}")
    await auth_client.delete(f"/projects/{project_id}")

# Test dashboard endpoints
@pytest.mark.asyncio
async def test_dashboard_endpoints(auth_client):
    # Test dashboard stats
    response = await auth_client.get("/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert isinstance(stats["total_test_cases"], int)
    assert isinstance(stats["total_executions"], int)
    
    # Test activity feed
    response = await auth_client.get("/dashboard/activity")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, list)

# Run the tests
if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main(["-v", "test_endpoints.py"]))
