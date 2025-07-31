import sys
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Set up logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auth_test.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('auth_test')

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import required modules
try:
    import httpx
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine, text
    from app.main import app
    from app.db.session import DATABASE_URL
    from app.core.security import get_password_hash, verify_password
    from app.auth.security import AuthService
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    
    logger.info("Successfully imported required modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

# Create a test client for the FastAPI app
client = TestClient(app)

# Database connection for direct queries
engine = create_engine(
    str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://"),
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_password_hashing():
    """Test password hashing and verification"""
    logger.info("Testing password hashing and verification...")
    
    # Test password
    password = "test123"
    hashed_password = get_password_hash(password)
    
    # Verify the password
    assert verify_password(password, hashed_password), "Password verification failed"
    assert not verify_password("wrongpassword", hashed_password), "Incorrect password verification"
    
    logger.info("Password hashing and verification tests passed")

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from the database"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM public.users WHERE email = :email"),
            {"email": email}
        )
        user = result.mappings().first()
        return dict(user) if user else None

def test_user_authentication():
    """Test user authentication with the API"""
    logger.info("=== Starting API Authentication Test ===")
    
    # Get a test user from the database
    test_email = "admin@example.com"
    logger.info(f"Looking for test user: {test_email}")
    
    user = get_user_by_email(test_email)
    
    if not user:
        logger.warning(f"❌ Test user {test_email} not found in the database")
        logger.info("=== API Authentication Test Failed: User not found ===")
        return False
    
    logger.info(f"✅ Found test user in database: {user}")
    
    # Test login with correct credentials
    login_data = {
        "username": test_email,
        "password": "test123"  # This is just an example, in a real test you'd need the actual password
    }
    logger.info(f"Prepared login data for {test_email}")
    
    try:
        # Test the login endpoint - using OAuth2 form data
        logger.info("\n=== Attempting to authenticate ===")
        logger.info(f"API Endpoint: /api/v1/auth/login")
        logger.info(f"Request Headers: {{'Content-Type': 'application/x-www-form-urlencoded'}}")
        logger.info(f"Request Data: {login_data}")
        
        # Make the request with form data
        try:
            response = client.post(
                "/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            logger.info("✅ Successfully received response from server")
        except Exception as e:
            logger.error(f"❌ Failed to make request to /api/v1/auth/login: {str(e)}")
            logger.info("=== API Authentication Test Failed: Request failed ===")
            return False
        
        # Log the raw response
        logger.info(f"\n=== Server Response ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Body: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"❌ Login failed with status code: {response.status_code}")
            logger.info("=== API Authentication Test Failed: Invalid status code ===")
            return False
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            token_type = data.get("token_type", "bearer")
            
            logger.info("Login successful!")
            logger.info(f"Access token: {access_token[:30]}..." if access_token else "No access token")
            
            # Test getting the current user with the access token
            headers = {"Authorization": f"{token_type} {access_token}"}
            user_response = client.get("/api/v1/auth/me", headers=headers)
            logger.info(f"Current user response: {user_response.status_code}")
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"Authenticated as: {user_data.get('email')}")
                return True
            else:
                logger.error(f"Failed to get current user: {user_response.text}")
                return False
        else:
            logger.error(f"Login failed: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error during authentication test: {str(e)}", exc_info=True)
        return False

async def test_auth_service():
    """Test the AuthService directly"""
    logger.info("Testing AuthService...")
    
    db = next(get_db_session())
    auth_service = AuthService(db)
    
    # Test with a known user
    test_email = "admin@example.com"
    
    try:
        # Test authenticate_user method (note: it's async)
        user = await auth_service.authenticate_user(test_email, "test123")
        if user:
            logger.info(f"Successfully authenticated user: {user['email']}")
            return True
        else:
            logger.error("Authentication failed: Invalid credentials")
            return False
            
    except Exception as e:
        logger.error(f"Error in AuthService test: {str(e)}", exc_info=True)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import asyncio
    
    logger.info("Starting authentication tests...")
    
    try:
        # Test password hashing
        test_password_hashing()
        
        # Run async tests in an event loop
        loop = asyncio.get_event_loop()
        
        # Test direct authentication with AuthService
        auth_service_result = loop.run_until_complete(test_auth_service())
        
        # Test API authentication
        api_auth_result = test_user_authentication()
        
        # Print summary
        logger.info("\n=== Test Results ===")
        logger.info(f"Password Hashing: PASSED")
        logger.info(f"AuthService Authentication: {"PASSED" if auth_service_result else "FAILED"}")
        logger.info(f"API Authentication: {"PASSED" if api_auth_result else "FAILED"}")
        
        if auth_service_result and api_auth_result:
            logger.info("\n✅ All authentication tests completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n❌ Some authentication tests failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during authentication tests: {str(e)}", exc_info=True)
        sys.exit(1)
