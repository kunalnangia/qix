"""Minimal debug script to identify the root cause of the TypeError."""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the app directly to check for initialization issues
print("=== Importing FastAPI app ===")
try:
    from backend.server import app
    print("✓ Successfully imported FastAPI app")
except Exception as e:
    print(f"✗ Error importing FastAPI app: {e}")
    raise

# Check if we can create a test client
print("\n=== Creating test client ===")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    print("✓ Successfully created test client")
except Exception as e:
    print(f"✗ Error creating test client: {e}")
    raise

# Test a simple endpoint
print("\n=== Testing health check endpoint ===")
try:
    response = client.get("/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ Successfully called health check endpoint")
except Exception as e:
    print(f"✗ Error calling health check endpoint: {e}")
    raise

print("\nDebug test completed successfully!")
