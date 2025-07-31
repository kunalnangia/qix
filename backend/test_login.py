import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = f"{BASE_URL}/api/auth/login"

# Test credentials
test_credentials = {
    "email": "test@gmail.com",
    "password": "test1234"
}

def test_login():
    print("Testing login endpoint...")
    try:
        # Make the login request
        response = requests.post(
            LOGIN_ENDPOINT,
            json=test_credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        # Try to parse the response as JSON
        try:
            response_json = response.json()
            print("Response JSON:")
            print(json.dumps(response_json, indent=2))
            
            if response.status_code == 200:
                print("\nLogin successful!")
                print(f"Access Token: {response_json.get('access_token')}")
            else:
                print(f"\nLogin failed: {response_json.get('detail', 'Unknown error')}")
                
        except ValueError:
            print("Response is not valid JSON")
            print(f"Response content: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    # Check if the API is running
    try:
        health_response = requests.get(f"{BASE_URL}/api/health")
        print(f"API Health Check: {health_response.status_code}")
        print(health_response.json())
        print("\n")
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to API: {str(e)}")
        print("Make sure the FastAPI server is running on port 8001")
        exit(1)
    
    # Run the login test
    test_login()
