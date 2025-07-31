import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = str(Path(__file__).parent / '.env')
load_dotenv(env_path)

class APITestClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        
    def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        if headers is None:
            headers = {}
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(kwargs.pop('headers', {}))
        
        logger.info(f"{method.upper()} {url}")
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Log response
            logger.debug(f"Status: {response.status_code}")
            
            try:
                data = response.json()
                logger.debug(f"Response: {json.dumps(data, indent=2, default=str)}")
                return {
                    'status_code': response.status_code,
                    'data': data,
                    'success': 200 <= response.status_code < 300
                }
            except ValueError:
                return {
                    'status_code': response.status_code,
                    'text': response.text,
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return {
                'status_code': 0,
                'error': str(e),
                'success': False
            }
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        if data is not None:
            kwargs['json'] = data
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        if data is not None:
            kwargs['json'] = data
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.request('DELETE', endpoint, **kwargs)
    
    def login(self, email: str, password: str) -> bool:
        """Login and store the JWT token"""
        response = self.post(
            "/api/v1/auth/login",
            data={"email": email, "password": password}
        )
        
        if response['success'] and 'access_token' in response['data']:
            self.token = response['data']['access_token']
            logger.info("✅ Login successful")
            return True
        else:
            logger.error(f"❌ Login failed: {response.get('data', {}).get('detail', 'Unknown error')}")
            return False

def test_health_check(client: APITestClient) -> bool:
    """Test the health check endpoint"""
    logger.info("\n🔍 Testing health check endpoint...")
    response = client.get("/api/v1/health")
    
    if not response['success']:
        logger.error(f"❌ Health check failed: {response.get('data', {}).get('detail', 'Unknown error')}")
        return False
    
    logger.info(f"✅ Health check passed: {response['data']}")
    return True

def test_public_endpoints(client: APITestClient) -> bool:
    """Test public API endpoints"""
    logger.info("\n🔍 Testing public endpoints...")
    
    # Test get current user (should fail without auth)
    response = client.get("/api/v1/users/me")
    if response['status_code'] != 401:
        logger.error("❌ Unauthenticated access to protected endpoint should fail")
        return False
    
    logger.info("✅ Public endpoint tests passed")
    return True

def test_authentication(client: APITestClient) -> bool:
    """Test authentication endpoints"""
    logger.info("\n🔍 Testing authentication...")
    
    # Try to login with invalid credentials
    response = client.post(
        "/api/v1/auth/login",
        data={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    if response['success'] or response['status_code'] != 401:
        logger.error("❌ Login with invalid credentials should fail")
        return False
    
    # Login with valid credentials (replace with test user)
    if not client.login("test@example.com", "testpassword"):
        # If test user doesn't exist, try to register first
        logger.info("Test user not found, attempting to register...")
        response = client.post(
            "/api/v1/auth/register",
            data={
                "email": "test@example.com",
                "password": "testpassword",
                "full_name": "Test User"
            }
        )
        
        if not response['success']:
            logger.error(f"❌ Failed to register test user: {response.get('data', {}).get('detail', 'Unknown error')}")
            return False
        
        # Try to login again
        if not client.login("test@example.com", "testpassword"):
            return False
    
    # Test getting current user (should work when authenticated)
    response = client.get("/api/v1/users/me")
    if not response['success']:
        logger.error(f"❌ Failed to get current user: {response.get('data', {}).get('detail', 'Unknown error')}")
        return False
    
    logger.info(f"✅ Authentication tests passed. Logged in as: {response['data'].get('email')}")
    return True

def test_projects_crud(client: APITestClient) -> bool:
    """Test CRUD operations for projects"""
    logger.info("\n🔍 Testing projects CRUD...")
    
    # Create a new project
    project_data = {
        "name": "Test Project",
        "description": "This is a test project"
    }
    
    # Create
    response = client.post("/api/v1/projects/", data=project_data)
    if not response['success']:
        logger.error(f"❌ Failed to create project: {response.get('data', {}).get('detail', 'Unknown error')}")
        return False
    
    project = response['data']
    project_id = project['id']
    logger.info(f"✅ Created project: {project['name']} (ID: {project_id})")
    
    # Read
    response = client.get(f"/api/v1/projects/{project_id}")
    if not response['success'] or response['data']['id'] != project_id:
        logger.error("❌ Failed to retrieve project")
        return False
    
    # Update
    update_data = {"name": "Updated Test Project"}
    response = client.put(f"/api/v1/projects/{project_id}", data=update_data)
    if not response['success'] or response['data']['name'] != update_data['name']:
        logger.error("❌ Failed to update project")
        return False
    
    # List
    response = client.get("/api/v1/projects/")
    if not response['success'] or not isinstance(response['data'], list):
        logger.error("❌ Failed to list projects")
        return False
    
    # Delete
    response = client.delete(f"/api/v1/projects/{project_id}")
    if not response['success']:
        logger.error("❌ Failed to delete project")
        return False
    
    # Verify deletion
    response = client.get(f"/api/v1/projects/{project_id}")
    if response['success']:
        logger.error("❌ Project was not deleted")
        return False
    
    logger.info("✅ Projects CRUD tests passed")
    return True

def main():
    # Initialize test client
    base_url = os.getenv("API_BASE_URL", "http://localhost:8001")
    client = APITestClient(base_url=base_url)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check, client),
        ("Public Endpoints", test_public_endpoints, client),
        ("Authentication", test_authentication, client),
        ("Projects CRUD", test_projects_crud, client)
    ]
    
    results = []
    for name, test_func, *args in tests:
        logger.info(f"\n{'='*40} {name} {'='*(40-len(name))}")
        success = test_func(*args)
        results.append((name, success))
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    all_passed = all(success for _, success in results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} - {name}")
    
    if all_passed:
        logger.info("\n✨ All tests passed successfully!")
    else:
        logger.info("\n❌ Some tests failed. Please check the error messages above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
