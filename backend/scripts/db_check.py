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

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sqlalchemy import create_engine, text
    from app.core.config import settings
    logger.info("✅ Successfully imported required modules")
except ImportError as e:
    logger.error(f"❌ Failed to import required modules: {e}")
    raise

def check_database():
    """Check database connection and list tables"""
    try:
        # Get database URL from settings
        db_url = settings.DATABASE_URI
        logger.info(f"Database URL: {db_url}")
        
        # Create engine with current settings
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            # Get database version
            version = conn.execute(text("SELECT version();")).scalar()
            logger.info(f"✅ Successfully connected to database!")
            logger.info(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            
            tables = [row[0] for row in result.fetchall()]
            if tables:
                logger.info("\nTables in the database:")
                for table in sorted(tables):
                    logger.info(f"- {table}")
            else:
                logger.warning("No tables found in the database")
                
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {str(e)}")
        return False
    
    return True

def check_test_user():
    """Check if test user exists in the database"""
    try:
        # Get database URL from settings
        db_url = settings.DATABASE_URI
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if users table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            
            if not result.scalar():
                logger.warning("❌ Users table does not exist in the database")
                return False
                
            # Check for test user
            result = conn.execute(text("""
                SELECT id, email, full_name, role, is_active 
                FROM users 
                WHERE email = 'test@gmail.com';
            
            user = result.fetchone()
            if user:
                logger.info("\n✅ Test user found:")
                logger.info(f"   ID: {user[0]}")
                logger.info(f"   Email: {user[1]}")
                logger.info(f"   Name: {user[2]}")
                logger.info(f"   Role: {user[3]}")
                logger.info(f"   Active: {user[4]}")
                return True
            else:
                logger.warning("❌ Test user (test@gmail.com) not found")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error checking for test user: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Database Check ===")
    
    # Check database connection
    if not check_database():
        logger.error("❌ Database check failed")
        sys.exit(1)
    
    # Check test user
    if not check_test_user():
        logger.warning("\nWould you like to create a test user? (y/n): ")
        if input().lower() == 'y':
            # Create test user
            from app.core.security import get_password_hash
            from datetime import datetime
            import uuid
            
            try:
                db_url = settings.DATABASE_URI
                engine = create_engine(db_url)
                
                with engine.connect() as conn:
                    # Create test user
                    user_id = str(uuid.uuid4())
                    hashed_password = get_password_hash("test1234")
                    created_at = datetime.utcnow()
                    
                    conn.execute(text("""
                        INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at)
                        VALUES (:id, :email, :hashed_password, :full_name, :role, :is_active, :created_at, :updated_at)
                    
                    ), {
                        'id': user_id,
                        'email': 'test@gmail.com',
                        'hashed_password': hashed_password,
                        'full_name': 'Test User',
                        'role': 'tester',
                        'is_active': True,
                        'created_at': created_at,
                        'updated_at': created_at
                    })
                    conn.commit()
                    
                    logger.info("\n✅ Test user created successfully!")
                    logger.info(f"   Email: test@gmail.com")
                    logger.info(f"   Password: test1234")
                    
            except Exception as e:
                logger.error(f"❌ Error creating test user: {str(e)}")
                sys.exit(1)
    
    logger.info("\n=== Check Complete ===")