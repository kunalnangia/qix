import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_login():
    # Get API base URL from environment variables or use default
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8001")
    login_url = f"{api_base_url}/api/v1/auth/login"
    
    # Test user credentials from environment variables
    test_user = {
        "username": os.getenv("TEST_USER_EMAIL", "test@example.com"),
        "password": os.getenv("TEST_USER_PASSWORD", "test1234")
    }
    
    print("=" * 80)
    print("TESTING LOGIN ENDPOINT")
    print("=" * 80)
    print(f"API URL: {login_url}")
    print(f"Testing with user: {test_user['username']}")
    
    try:
        # Make login request
        response = requests.post(login_url, json=test_user)
        
        # Print response details
        print("\nResponse Status Code:", response.status_code)
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        # Try to parse JSON response
        try:
            json_response = response.json()
            print("\nResponse JSON:")
            print(json_response)
            
            # Check if login was successful
            if response.status_code == 200 and "access_token" in json_response:
                print("\n✅ Login successful!")
                print(f"Access token: {json_response['access_token'][:20]}...")
                return True
            else:
                print("\n❌ Login failed!")
                if "detail" in json_response:
                    print(f"Error: {json_response['detail']}")
                return False
                
        except ValueError:
            print("\n❌ Failed to parse JSON response:")
            print(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ LOGIN TEST COMPLETED SUCCESSFULLY")
    else:
        print("❌ LOGIN TEST FAILED")
    print("=" * 80)
