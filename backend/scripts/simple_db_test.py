import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import required modules
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.db.session import SQLALCHEMY_DATABASE_URL
    from datetime import datetime
    
    logger.info("All required modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

def test_connection():
    """Test database connection and basic operations"""
    try:
        # Create a synchronous engine for testing
        sync_db_url = str(SQLALCHEMY_DATABASE_URL).replace("asyncpg", "psycopg2")
        logger.info(f"Testing connection to database: {sync_db_url}")
        
        engine = create_engine(
            sync_db_url,
            echo=True  # Enable SQL echo for debugging
        )
        
        # Test connection and list tables
        with engine.connect() as conn:
            # Get database version
            version = conn.execute(text("SELECT version()")).scalar()
            logger.info(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            logger.info(f"Tables in database: {tables}")
            
            # Check if users table exists
            if 'users' in tables:
                logger.info("Users table exists")
                
                # Count users
                count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                logger.info(f"Number of users: {count}")
                
                # Try to insert a test user
                test_email = f"test_{int(datetime.now().timestamp())}@example.com"
                logger.info(f"Attempting to insert test user: {test_email}")
                
                conn.execute(
                    text(
                        """
                        INSERT INTO users (email, full_name, hashed_password, role, is_active, created_at, updated_at)
                        VALUES (:email, :full_name, :hashed_password, :role, :is_active, :created_at, :updated_at)
                        """
                    ),
                    {
                        "email": test_email,
                        "full_name": "Test User",
                        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # hashed "test123"
                        "role": "tester",
                        "is_active": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                conn.commit()
                logger.info("Test user inserted successfully")
                
                # Verify insertion
                new_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                logger.info(f"Number of users after insertion: {new_count}")
                
            else:
                logger.warning("Users table does not exist")
                
    except Exception as e:
        logger.error(f"Error during database operations: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Starting database connection test...")
    test_connection()
    logger.info("Test completed")
