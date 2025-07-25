"""Test FastAPI application without database dependencies."""
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
    assert response.status_code == 200
    print("✓ Root endpoint works")

def test_nonexistent_route():
    """Test a non-existent route."""
    print("\n=== Testing non-existent route ===")
    response = client.get("/nonexistent-route")
    assert response.status_code == 404
    print("✓ Non-existent route returns 404")

if __name__ == "__main__":
    print("Running FastAPI tests without database...")
    test_read_root()
    test_nonexistent_route()
    print("\nAll tests completed!")
