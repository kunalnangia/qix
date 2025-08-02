import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8001/api/v1"

def print_response(response, description):
    """Print the response details in a formatted way"""
    print(f"\n=== {description} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)
    return response

def test_project_endpoints():
    """Test project CRUD endpoints"""
    # Test data
    project_data = {
        "name": "Test Project",
        "description": "Test project for API testing",
        "is_active": True
    }
    
    # 1. Create a new project
    print("\n1. Creating a new project...")
    response = requests.post(
        f"{BASE_URL}/projects",
        json=project_data
    )
    response = print_response(response, "Create Project")
    
    if response.status_code != 201:
        print("Failed to create test project. Aborting tests.")
        return
    
    project_id = response.json()["id"]
    print(f"Created project with ID: {project_id}")
    
    # 2. Get the created project
    print("\n2. Getting the created project...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    print_response(response, "Get Project")
    
    # 3. Update the project
    print("\n3. Updating the project...")
    update_data = {
        "name": "Updated Test Project",
        "description": "Updated description",
        "is_active": False
    }
    response = requests.put(
        f"{BASE_URL}/projects/{project_id}",
        json=update_data
    )
    print_response(response, "Update Project")
    
    # 4. Verify the update
    print("\n4. Verifying the update...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    response = print_response(response, "Verify Update")
    
    # 5. Delete the project
    print("\n5. Deleting the project...")
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    print_response(response, "Delete Project")
    
    # 6. Verify deletion
    print("\n6. Verifying deletion...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    print_response(response, "Verify Deletion")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_project_endpoints()
