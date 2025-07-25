"""Direct test of FastAPI application without using pytest."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from backend.server import app

# Create a test client
from fastapi.testclient import TestClient
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

def test_root():
    """Test the root endpoint."""
    print("\n=== Testing root endpoint ===")
    response = client.get("/")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:100]}...")
    assert response.status_code == 200
    assert "Emergent IntelliTest" in response.text
    print("✓ Root endpoint passed")

if __name__ == "__main__":
    print("Starting direct tests...")
    try:
        test_health_check()
        test_root()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        raise
