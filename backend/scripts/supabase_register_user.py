import os
import sys
import json
import requests
from dotenv import load_dotenv

def register_user():
    print("Registering test user using Supabase Auth API...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase URL and service key from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        return False
    
    # Test user details
    user_email = "test@example.com"
    user_password = "test1234"
    
    # Supabase Auth API endpoint for signup
    auth_url = f"{supabase_url}/auth/v1/admin/users"
    
    # Headers for the request
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    # User data
    user_data = {
        "email": user_email,
        "password": user_password,
        "email_confirm": True,  # Skip email confirmation
        "user_metadata": {
            "name": "Test User",
            "username": user_email.split('@')[0]
        },
        "app_metadata": {
            "provider": "email",
            "providers": ["email"]
        }
    }
    
    try:
        # Make the request to create the user
        response = requests.post(
            auth_url,
            headers=headers,
            json=user_data
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            user = response.json()
            print("✅ Successfully registered test user:")
            print(f"ID: {user.get('id')}")
            print(f"Email: {user.get('email')}")
            print(f"Password: {user_password}")
            return True
        else:
            print(f"❌ Error registering user: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    register_user()
