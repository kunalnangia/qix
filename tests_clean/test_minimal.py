"""Minimal test for FastAPI application."""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import FastAPI and create a test client
from fastapi.testclient import TestClient
from backend.server import app

# Create a test client
client = TestClient(app)

def test_read_root():
    """Test the root endpoint."""
    print("\n=== Testing root endpoint ===")
    response = client.get("/")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200
    print("✓ Root endpoint works")

if __name__ == "__main__":
    print("Running minimal test...")
    test_read_root()
    print("\nTest completed!")
