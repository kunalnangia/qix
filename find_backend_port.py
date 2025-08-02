import requests
import sys

def test_backend_port(port):
    base_url = f"http://localhost:{port}/api/v1"
    print(f"\nTesting port {port}...")
    
    try:
        # Test health check
        print("  Testing health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"  Health check status: {response.status_code}")
        print(f"  Response: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Connection failed: {e}")
        return False

def main():
    print("Searching for backend server...")
    
    # Common ports to check
    ports_to_try = [8001, 3000, 5000, 8002]
    
    for port in ports_to_try:
        if test_backend_port(port):
            print(f"\n✅ Backend server found on port {port}")
            print(f"   You can access it at: http://localhost:{port}")
            print(f"   API base URL: http://localhost:{port}/api/v1")
            sys.exit(0)
    
    print("\n❌ Could not find a running backend server on common ports.")
    print("   Make sure the backend server is running and accessible.")
    sys.exit(1)

if __name__ == "__main__":
    main()
