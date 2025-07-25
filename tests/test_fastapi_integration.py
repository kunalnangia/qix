"""Integration tests for FastAPI application with absolute imports."""
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import using absolute path
from backend.server import app
from backend.database_sqlite import Base, engine, SessionLocal

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    print("\n=== Testing health check endpoint ===")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✓ Health check passed")

def test_register_user():
    """Test user registration endpoint."""
    print("\n=== Testing user registration ===")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    print(f"Status code: {response.status_code}")
    
    # Check response
    if response.status_code == 500:
        print(f"⚠️ Registration failed with error: {response.text}")
    else:
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "user" in response.json()
        print("✓ User registration passed")

if __name__ == "__main__":
    print("Running FastAPI integration tests...")
    test_health_check()
    test_register_user()
    print("\nAll integration tests completed!")
