import sys
import os
import logging
from pathlib import Path

# Directly set up basic logging to file and console
log_file = 'direct_db_test.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),  # Write to file
        logging.StreamHandler(sys.stdout)         # Also log to console
    ]
)
logger = logging.getLogger('direct_db_test')

def main():
    logger.info("Starting direct database test...")
    
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent.parent)
    sys.path.append(project_root)
    
    try:
        # Import required modules
        from sqlalchemy import create_engine, text
        from app.db.session import DATABASE_URL, engine
        
        logger.info("Successfully imported required modules")
        logger.info(f"Database URL from session: {DATABASE_URL}")
        
        # Create a synchronous engine
        sync_db_url = str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://")
        logger.info(f"Synchronous DB URL: {sync_db_url}")
        
        # Create a new engine to test with
        test_engine = create_engine(sync_db_url)
        
        # Test connection with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with test_engine.connect() as conn:
                    logger.info(f"Connection attempt {attempt + 1}/{max_retries}")
                    
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
                    logger.info(f"Users table exists in public schema: {users_table_exists}")
                    
                    if users_table_exists:
                        # Count users
                        result = conn.execute(text("SELECT COUNT(*) FROM public.users"))
                        count = result.scalar()
                        logger.info(f"Number of users in public.users: {count}")
                        
                        # Get first few users if any exist
                        if count > 0:
                            result = conn.execute(text("SELECT id, email, is_active FROM public.users LIMIT 5"))
                            users = [dict(row) for row in result.mappings()]
                            logger.info(f"Sample users: {users}")
                    
                    # Check auth schema as well
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'auth' 
                            AND table_name = 'users'
                        )
                    """))
                    
                    auth_users_table_exists = result.scalar()
                    logger.info(f"Users table exists in auth schema: {auth_users_table_exists}")
                    
                    if auth_users_table_exists:
                        # Count users in auth schema
                        result = conn.execute(text("SELECT COUNT(*) FROM auth.users"))
                        count = result.scalar()
                        logger.info(f"Number of users in auth.users: {count}")
                        
                        # Get first few users if any exist
                        if count > 0:
                            result = conn.execute(text("SELECT id, email, raw_user_meta_data FROM auth.users LIMIT 5"))
                            users = [dict(row) for row in result.mappings()]
                            # Don't log sensitive data
                            logger.info(f"Found {len(users)} users in auth.users")
                    
                    break  # If we got here, connection was successful
                    
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    logger.error("Max retries reached. Giving up.")
                    raise
                logger.info(f"Retrying in 2 seconds... (attempt {attempt + 2}/{max_retries})")
                import time
                time.sleep(2)
        
        logger.info("Direct database test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during direct database test: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
        sys.exit(1)
