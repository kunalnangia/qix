import sys
import os
import logging
from pathlib import Path

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Import required modules
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.db.session import SQLALCHEMY_DATABASE_URL
    from app.models.db_models import User
    from app.core.security import get_password_hash
    from datetime import datetime
    
    logger.info("All required modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

def test_db_connection():
    """Test database connection and insert a test user"""
    try:
        # Create a synchronous engine for testing
        sync_db_url = str(SQLALCHEMY_DATABASE_URL).replace("asyncpg", "psycopg2")
        logger.info(f"Testing connection to database: {sync_db_url}")
        
        # Log the environment variables being used
        logger.debug(f"SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")
        
        # Create engine with connection pool and timeout settings
        engine = create_engine(
            sync_db_url,
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=3600,   # Recycle connections after 1 hour
            pool_size=5,         # Number of connections to keep open
            max_overflow=10,     # Number of connections to allow in overflow
            echo=True           # Enable SQL echo for debugging
        )
        
        # Test connection with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                with engine.connect() as conn:
                    # Get database version
                    logger.info(f"Connection attempt {attempt + 1}/{max_retries}")
                    version = conn.execute(text("SELECT version()")).scalar()
                    logger.info(f"✅ Successfully connected to database. Version: {version}")
                    
                    # Check if users table exists
                    logger.info("Checking if users table exists...")
                    result = conn.execute(
                        text(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = 'users'
                            )
                            """
                        )
                    )
                    users_table_exists = result.scalar()
                    logger.info(f"Users table exists: {users_table_exists}")
                    
                    if users_table_exists:
                        # Count existing users
                        count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                        logger.info(f"Current number of users in database: {count}")
                        
                        # List first few users if any exist
                        if count > 0:
                            users = conn.execute(
                                text("SELECT id, email, is_active FROM users LIMIT 5")
                            ).fetchall()
                            logger.info(f"Sample users: {[dict(user) for user in users]}")
                    else:
                        logger.warning("Users table does not exist in the public schema")
                        
                    break  # If we got here, connection was successful
                    
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    logger.error("Max retries reached. Giving up.")
                    raise
                logger.info(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
        
        # Create a session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # Create a test user
            test_email = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
            logger.info(f"Creating test user: {test_email}")
            
            user = User(
                email=test_email,
                full_name="Test User",
                hashed_password=get_password_hash("test123"),
                role="tester",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(user)
            session.commit()
            logger.info(f"Successfully created user with ID: {user.id}")
            
            # Verify the user was inserted
            with engine.connect() as conn:
                count_after = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                logger.info(f"Number of users after insertion: {count_after}")
                
                # Get the inserted user
                result = conn.execute(
                    text("SELECT email, full_name FROM users WHERE id = :id"),
                    {"id": user.id}
                ).fetchone()
                
                if result:
                    logger.info(f"Found user in database: {dict(result)}")
                else:
                    logger.warning("Could not find the inserted user in the database")
                    
        except Exception as e:
            logger.error(f"Error during database operations: {e}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Starting database connection test...")
    test_db_connection()
    logger.info("Test completed")
