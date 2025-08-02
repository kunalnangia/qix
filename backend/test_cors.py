import requests

def test_endpoint(url, method='GET', headers=None, data=None):
    print(f"\nTesting {method} request to {url}")
    
    # Default headers
    default_headers = {
        'Origin': 'http://localhost:5175',
        'Content-Type': 'application/json'
    }
    
    # Update with any custom headers
    if headers:
        default_headers.update(headers)
    
    try:
        # Make the request
        if method.upper() == 'GET':
            response = requests.get(url, headers=default_headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=default_headers, json=data)
        elif method.upper() == 'OPTIONS':
            response = requests.options(url, headers=default_headers)
        else:
            print(f"Unsupported method: {method}")
            return
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        # Try to parse JSON response if possible
        try:
            print("Response Body:", response.json())
        except ValueError:
            print("Response Body:", response.text)
        
        return response
        
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def test_cors():
    base_url = "http://127.0.0.1:8001"
    
    # 1. Test GET request to root endpoint
    test_endpoint(f"{base_url}/")
    
    # 2. Test OPTIONS preflight request
    test_endpoint(
        f"{base_url}/",
        method='OPTIONS',
        headers={
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'content-type'
        }
    )
    
    # 3. Test POST request (simulate frontend API call)
    test_endpoint(
        f"{base_url}/api/v1/auth/register",
        method='POST',
        data={
            'email': 'test@example.com',
            'password': 'testpassword',
            'full_name': 'Test User'
        }
    )
    
    # 4. Test with different origin
    test_endpoint(
        f"{base_url}/",
        headers={'Origin': 'http://localhost:5175'}
    )

if __name__ == "__main__":
    test_cors()
