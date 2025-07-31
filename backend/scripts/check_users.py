import sys
import os
import logging
from pathlib import Path

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
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.models.db_models import User
    logger.info("✅ Successfully imported required modules")
except ImportError as e:
    logger.error(f"❌ Failed to import required modules: {e}")
    raise

def check_users():
    """List all users in the database using settings from .env"""
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
            # Query all users
            users = db.query(User).order_by(User.email).all()
            
            if not users:
                logger.warning("No users found in the database")
                return
                
            logger.info(f"Found {len(users)} user(s) in the database:")
            logger.info("-" * 80)
            
            for user in users:
                logger.info(f"ID: {user.id}")
                logger.info(f"Email: {user.email}")
                logger.info(f"Full Name: {user.full_name}")
                logger.info(f"Role: {user.role}")
                logger.info(f"Is Active: {user.is_active}")
                logger.info(f"Created At: {user.created_at}")
                logger.info("-" * 80)
                
        except Exception as e:
            logger.error(f"❌ Error querying users: {str(e)}")
            return False
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    logger.info("=== Starting User List Check ===")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    if check_users():
        logger.info("✅ User list check completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ User list check failed")
        sys.exit(1)
