import sys
import os
import logging
from pathlib import Path
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy import create_engine
    from app.core.config import settings
    from app.models.db_models import User
    from app.core.security import get_password_hash
    logger.info("✅ Successfully imported required modules")
except ImportError as e:
    logger.error(f"❌ Failed to import required modules: {e}")
    raise

def create_test_user():
    """Create a test user directly in the database using settings from .env"""
    try:
        # Get database URL from environment variables
        db_url = settings.DATABASE_URI
        logger.info(f"Connecting to database: {db_url}")
        
        # Create a synchronous engine
        engine = create_engine(
            db_url,
            echo=True
        )
        
        # Create a session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if test user already exists
            test_email = os.getenv("TEST_USER_EMAIL", "test@example.com")
            test_password = os.getenv("TEST_USER_PASSWORD", "test1234")
            
            existing_user = db.query(User).filter(User.email == test_email).first()
            
            if existing_user:
                logger.warning(f"Test user already exists with email: {test_email}")
                logger.info(f"User ID: {existing_user.id}")
                return existing_user
                
            # Create new test user
            user = User(
                id=str(uuid.uuid4()),
                email=test_email,
                hashed_password=get_password_hash(test_password),
                full_name=os.getenv("TEST_USER_NAME", "Test User"),
                role=os.getenv("TEST_USER_ROLE", "tester"),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info("✅ Successfully created test user:")
            logger.info(f"   ID: {user.id}")
            logger.info(f"   Email: {user.email}")
            logger.info(f"   Password: {test_password}")
            logger.info(f"   Role: {user.role}")
            
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating test user: {str(e)}")
            return None
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {str(e)}")
        return None

if __name__ == "__main__":
    logger.info("=== Starting Test User Creation ===")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    user = create_test_user()
    
    if user:
        logger.info("✅ Test user creation/retrieval completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Failed to create/retrieve test user")
        sys.exit(1)
