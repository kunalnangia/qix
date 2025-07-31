import sys
import os
import logging
from pathlib import Path

# Directly set up basic logging to file and console
log_file = 'minimal_test.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),  # Write to file
        logging.StreamHandler(sys.stdout)         # Also log to console
    ]
)
logger = logging.getLogger('minimal_test')

def main():
    logger.info("Starting minimal database test...")
    
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent.parent)
    sys.path.append(project_root)
    
    try:
        # Try to import required modules
        from sqlalchemy import create_engine, text
        from app.db.session import SQLALCHEMY_DATABASE_URL
        
        logger.info("Successfully imported required modules")
        logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
        
        # Create a synchronous engine
        sync_db_url = str(SQLALCHEMY_DATABASE_URL).replace("asyncpg", "psycopg2")
        logger.info(f"Synchronous DB URL: {sync_db_url}")
        
        engine = create_engine(sync_db_url)
        
        # Test connection
        with engine.connect() as conn:
            logger.info("Successfully connected to the database")
            
            # Execute a simple query
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Test query result: {result.scalar()}")
            
            # Check if users table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """))
            
            users_table_exists = result.scalar()
            logger.info(f"Users table exists: {users_table_exists}")
            
            if users_table_exists:
                # Count users
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                logger.info(f"Number of users: {count}")
                
                # Get first few users if any exist
                if count > 0:
                    result = conn.execute(text("SELECT id, email FROM users LIMIT 5"))
                    users = [dict(row) for row in result.mappings()]
                    logger.info(f"Sample users: {users}")
        
        logger.info("Minimal test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during minimal test: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
        sys.exit(1)
