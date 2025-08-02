import requests
import json
from dotenv import load_dotenv
import os

def test_login():
    # Load environment variables
    load_dotenv()
    
    # Get the base URL from environment or use default
    base_url = os.getenv("BACKEND_URL", "http://localhost:8001/api/v1")
    
    # Test user credentials
    test_email = "test121@gmail.com"
    test_password = "testpassword"  # Replace with the actual password used during registration
    
    # Prepare login data
    login_data = {
        "username": test_email,
        "password": test_password
    }
    
    try:
        # Make the login request
        print(f"🔐 Attempting to log in as {test_email}...")
        response = requests.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Check the response
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print("\nAccess Token:")
            print("-" * 40)
            print(token_data["access_token"])
            print("\nToken Type:")
            print("-" * 40)
            print(token_data["token_type"])
            
            # Test a protected endpoint
            print("\n🔒 Testing protected endpoint...")
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            user_info = requests.get(f"{base_url}/users/me", headers=headers)
            
            if user_info.status_code == 200:
                print("✅ Successfully accessed protected endpoint!")
                print("\nUser Info:")
                print("-" * 40)
                print(json.dumps(user_info.json(), indent=2))
            else:
                print(f"❌ Failed to access protected endpoint. Status: {user_info.status_code}")
                print(user_info.text)
                
        else:
            print(f"❌ Login failed with status code: {response.status_code}")
            print("Response:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error making request: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_login()
