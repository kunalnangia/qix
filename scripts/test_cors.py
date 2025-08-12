import requests
import sys

def test_cors():
    url = "http://127.0.0.1:8001/api/v1/health"
    
    # Test OPTIONS request (preflight)
    print("Testing OPTIONS request (preflight)...")
    try:
        response = requests.options(
            url,
            headers={
                "Origin": "http://127.0.0.1:5174",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        print(f"OPTIONS Status Code: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control-'):
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"OPTIONS request failed: {e}")
        return False
    
    # Test GET request
    print("\nTesting GET request...")
    try:
        response = requests.get(
            url,
            headers={
                "Origin": "http://127.0.0.1:5174"
            }
        )
        print(f"GET Status Code: {response.status_code}"    )
        print(f"Response: {response.text}")
        print("Response Headers:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control-'):
                print(f"  {key}: {value}")
        return True
    except Exception as e:
        print(f"GET request failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing CORS configuration...\n")
    success = test_cors()
    if success:
        print("\n✅ CORS test passed!")
        sys.exit(0)
    else:
        print("\n❌ CORS test failed!")
        sys.exit(1)
