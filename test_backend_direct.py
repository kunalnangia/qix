import sys
import requests
from fastapi.testclient import TestClient

# Import the FastAPI app
sys.path.append('.')
from app.main import app

def test_backend_direct():
    # Test with TestClient (bypassing network)
    print("\n=== Testing with TestClient (no network) ===")
    client = TestClient(app)
    
    # Test health check endpoint
    print("\nTesting health check endpoint:")
    response = client.get("/api/v1/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test CORS headers
    print("\nTesting CORS headers:")
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://127.0.0.1:5174",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    print(f"OPTIONS Status: {response.status_code}")
    print("CORS Headers:")
    for key, value in response.headers.items():
        if key.lower().startswith('access-control-'):
            print(f"  {key}: {value}")

if __name__ == "__main__":
    print("Testing backend server directly...")
    test_backend_direct()
