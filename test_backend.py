import requests
import sys

def test_backend():
    base_url = "http://localhost:8001/api/v1"
    
    # Test health check
    print("Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test project listing
    print("\nTesting project listing...")
    try:
        response = requests.get(f"{base_url}/projects")
        print(f"Project list status: {response.status_code}")
        if response.status_code == 200:
            projects = response.json()
            print(f"Found {len(projects)} projects")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Project list failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting backend tests...")
    success = test_backend()
    if success:
        print("\n✅ Backend tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Backend tests failed!")
        sys.exit(1)
