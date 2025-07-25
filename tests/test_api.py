"""Test FastAPI application endpoints."""
from fastapi.testclient import TestClient
import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from backend.server import app

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_user():
    """Test user registration endpoint."""
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()

if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"])
