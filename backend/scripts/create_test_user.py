import requests
import json
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:8001/api/v1"

def create_test_user():
    """Create a test user"""
    url = f"{BASE_URL}/auth/register"
    
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
        "role": "tester"
    }
    
    try:
        response = requests.post(url, json=user_data)
        response.raise_for_status()
        print("User created successfully!")
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400 and "already exists" in e.response.text:
            print("User already exists, proceeding to login...")
            return None
        print(f"Error creating user: {e}")
        print(f"Response: {e.response.text}")
        return None

def login_user():
    """Login with test user credentials"""
    url = f"{BASE_URL}/auth/login"
    
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Note: Using data= instead of json= for form data
        response = requests.post(
            url,
            data={
                "username": login_data["username"],
                "password": login_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        
        token_data = response.json()
        print("\nLogin successful!")
        print(f"Access Token: {token_data['access_token']}")
        return token_data
    except requests.exceptions.HTTPError as e:
        print(f"\nLogin failed: {e}")
        print(f"Response: {e.response.text}")
        return None

def get_current_user(access_token: str):
    """Get current user info using the access token"""
    url = f"{BASE_URL}/users/me"
    
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        
        user_data = response.json()
        print("\nCurrent User Info:")
        pprint(user_data, indent=2)
        return user_data
    except requests.exceptions.HTTPError as e:
        print(f"\nFailed to get user info: {e}")
        print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    print("=== Creating Test User ===")
    user = create_test_user()
    
    print("\n=== Logging In ===")
    token_data = login_user()
    
    if token_data:
        print("\n=== Getting Current User Info ===")
        get_current_user(token_data["access_token"])
    
    print("\n=== Test Complete ===")
