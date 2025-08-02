import requests
import sys

def test_health_endpoint():
    url = "http://localhost:8001/health"
    print(f"Testing health endpoint at {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure the backend server is running")
        print("2. Check if the server is listening on the correct port (default: 8001)")
        print("3. Verify there are no firewall or network issues")
        print("4. Check server logs for any error messages")

if __name__ == "__main__":
    test_health_endpoint()
