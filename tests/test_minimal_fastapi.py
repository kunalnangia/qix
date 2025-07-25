"""Minimal FastAPI test with database."""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import FastAPI and create a test client
from fastapi.testclient import TestClient

# Import the database module first to ensure it's available
import backend.database_sqlite as db

# Now import the FastAPI app
from backend.server import app

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    print("\n=== Testing health check endpoint ===")
    response = client.get("/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✓ Health check passed")

if __name__ == "__main__":
    print("Running minimal FastAPI test...")
    test_health_check()
    print("\nTest completed!")
