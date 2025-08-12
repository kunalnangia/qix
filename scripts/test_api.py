import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health check: {e}")
        return False

def test_register_user():
    """Test user registration"""
    print("\nTesting user registration...")
    try:
        user_data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error testing user registration: {e}")
        return False

def test_get_projects(token):
    """Test getting projects with authentication"""
    print("\nTesting get projects...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/projects", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Found {len(response.json())} projects")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing get projects: {e}")
        return False

def test_get_test_cases(token):
    """Test getting test cases with authentication"""
    print("\nTesting get test cases...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/test-cases", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            test_cases = response.json()
            print(f"Found {len(test_cases)} test cases")
            if test_cases:
                print(f"First test case: {test_cases[0]['title']}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing get test cases: {e}")
        return False

def test_get_test_executions(token):
    """Test getting test executions with authentication"""
    print("\nTesting get test executions...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/test-executions", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            executions = response.json()
            print(f"Found {len(executions)} test executions")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing get test executions: {e}")
        return False

def test_get_dashboard_stats(token):
    """Test getting dashboard statistics"""
    print("\nTesting dashboard statistics...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/dashboard/stats", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print("Dashboard Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing dashboard statistics: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting API tests...")
    
    # Test health check
    if not test_health_check():
        print("Health check failed. Is the server running?")
        return
    
    # Test user registration
    if not test_register_user():
        print("User registration test failed. Continuing with other tests...")
    
    # For other tests, we need an authentication token
    # This is a placeholder - in a real test, you would log in and get a token
    token = ""
    
    if token:
        # Test authenticated endpoints
        test_get_projects(token)
        test_get_test_cases(token)
        test_get_test_executions(token)
        test_get_dashboard_stats(token)
    else:
        print("\nSkipping authenticated tests - no valid token available")

if __name__ == "__main__":
    main()
