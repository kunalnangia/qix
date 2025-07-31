"""
Script to check if the FastAPI application is running and accessible.
"""

import requests
import time
import sys

def check_fastapi():
    """Check if the FastAPI application is running and accessible."""
    url = "http://localhost:8001/api/v1/health"
    max_attempts = 3
    
    print(f"Checking FastAPI application at {url}")
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}/{max_attempts}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print("✅ FastAPI application is running and accessible!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"⚠️  Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            
        if attempt < max_attempts:
            print(f"Retrying in 2 seconds...")
            time.sleep(2)
    
    print("❌ Failed to connect to the FastAPI application")
    return False

if __name__ == "__main__":
    if not check_fastapi():
        sys.exit(1)
