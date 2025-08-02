import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Base URL for the FastAPI server
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check status code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health check: {e}")
        return False

def test_register_user():
    """Test user registration"""
    try:
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=user_data
        )
        print(f"Register status code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error testing registration: {e}")
        return False

if __name__ == "__main__":
    print("Testing FastAPI server...")
    print("\n1. Testing health check...")
    health_ok = test_health_check()
    
    print("\n2. Testing user registration...")
    register_ok = test_register_user()
    
    print("\nTest Results:")
    print(f"✅ Health Check: {'PASSED' if health_ok else '❌ FAILED'}")
    print(f"✅ User Registration: {'PASSED' if register_ok else '❌ FAILED'}")
