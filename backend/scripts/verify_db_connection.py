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

def main():
    """Main function to test database connection and list tables"""
    try:
        # Get database URL from settings
        db_url = settings.DATABASE_URI
        logger.info(f"Testing connection to: {db_url}")
        
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            # Get database version
            version = conn.execute(text("SELECT version();")).scalar()
            logger.info(f"✅ Connected to database!")
            logger.info(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            
            tables = [row[0] for row in result.fetchall()]
            if tables:
                logger.info("\nTables in the database:")
                for table in sorted(tables):
                    logger.info(f"- {table}")
            else:
                logger.warning("No tables found in the database")
            
            # Check if users table exists
            if 'users' in tables:
                logger.info("\nChecking for test user...")
                result = conn.execute(text("""
                    SELECT id, email, full_name, role, is_active 
                    FROM users 
                    WHERE email = 'test@gmail.com';
                
                user = result.fetchone()
                if user:
                    logger.info("✅ Test user found:")
                    logger.info(f"   ID: {user[0]}")
                    logger.info(f"   Email: {user[1]}")
                    logger.info(f"   Name: {user[2]}")
                    logger.info(f"   Role: {user[3]}")
                    logger.info(f"   Active: {user[4]}")
                else:
                    logger.warning("❌ Test user (test@gmail.com) not found")
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("=== Database Connection Test ===")
    if main():
        logger.info("✅ Test completed successfully!")
    else:
        logger.error("❌ Test failed")
        sys.exit(1)
