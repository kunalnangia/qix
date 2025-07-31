import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('check_admin_user')

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded environment from: {env_path}")

def get_db_connection():
    """Create a database connection using the DATABASE_URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    # For SQLAlchemy 1.4+, we need to use the asyncpg URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    
    logger.info(f"Connecting to database: {database_url}")
    engine = create_engine(database_url)
    return engine

def check_admin_user(engine):
    """Check if admin@example.com exists in the database"""
    with engine.connect() as conn:
        # Check in auth.users table (Supabase)
        result = conn.execute(
            text("SELECT * FROM auth.users WHERE email = :email"),
            {"email": "admin@example.com"}
        )
        user = result.mappings().first()
        
        if user:
            logger.info("✅ Found admin user in auth.users table:")
            logger.info(f"  ID: {user['id']}")
            logger.info(f"  Email: {user['email']}")
            logger.info(f"  Created At: {user['created_at']}")
            
            # Check if the password is set (not checking the actual password)
            if user.get('encrypted_password'):
                logger.info("  Password: Set")
            else:
                logger.warning("  Password: Not set")
            
            return True
        else:
            logger.warning("❌ Admin user not found in auth.users table")
            return False

def check_public_users(engine):
    """Check if there are any users in the public.users table"""
    with engine.connect() as conn:
        try:
            result = conn.execute(
                text("SELECT * FROM public.users LIMIT 5")
            )
            users = result.mappings().all()
            
            if users:
                logger.info("\nFound users in public.users table:")
                for i, user in enumerate(users, 1):
                    logger.info(f"  {i}. ID: {user.get('id')}, Email: {user.get('email')}")
                return True
            else:
                logger.warning("No users found in public.users table")
                return False
                
        except Exception as e:
            logger.error(f"Error checking public.users table: {str(e)}")
            return False

def main():
    try:
        # Load environment variables
        load_environment()
        
        # Create database connection
        engine = get_db_connection()
        
        # Check admin user
        logger.info("\n=== Checking for admin user ===")
        admin_exists = check_admin_user(engine)
        
        # Check public users
        logger.info("\n=== Checking public users table ===")
        check_public_users(engine)
        
        if not admin_exists:
            logger.warning("\n❌ Admin user not found. You may need to create it.")
        else:
            logger.info("\n✅ Admin user check completed successfully.")
        
        return 0 if admin_exists else 1
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
