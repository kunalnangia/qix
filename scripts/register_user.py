import requests
import json

# API endpoint
url = "http://localhost:3000/api/auth/register"

# User data
user_data = {
    "email": "test@gmail.com",
    "password": "test1234",  # Increased to 8 characters to meet requirements
    "full_name": "Test User"
}

try:
    # Make the POST request
    response = requests.post(url, json=user_data)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

except json.JSONDecodeError:
    print(f"Response could not be decoded as JSON. Raw response: {response.text}")
