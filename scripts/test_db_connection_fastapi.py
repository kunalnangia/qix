import os
import sys
import logging
from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('db_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
print(f"Loading environment from: {env_path}")
load_dotenv(env_path, override=True)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

print(f"Using database URL: {DATABASE_URL.split('@')[-1]}")

# Create engine with the same configuration as in session.py
engine = create_engine(
    str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://"),
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    pool_timeout=30,
    connect_args={
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
)

def test_connection():
    try:
        logger.info("Attempting to connect to the database...")
        logger.debug(f"Using database URL: {DATABASE_URL}")
        
        # Test the connection with a simple query first
        try:
            with engine.connect() as connection:
                logger.info("✅ Successfully connected to the database!")
                
                # Get database version
                logger.info("Fetching database version and info...")
                result = connection.execute(text("SELECT version(), current_database(), current_user, current_schema()"))
                db_version, db_name, db_user, current_schema = result.fetchone()
                
                print("\n📊 Database Connection Successful!")
                print("\n📋 Database Info:")
                print(f"   Name: {db_name}")
                print(f"   User: {db_user}")
                print(f"   Schema: {current_schema}")
                print(f"   Version: {db_version.split('on')[0].strip()}")
                
                # List all tables
                logger.info("Fetching list of tables...")
                result = connection.execute(text("""
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = :schema
                    ORDER BY table_name;
                """), {"schema": current_schema})
                
                tables = [(row[0], row[1]) for row in result.fetchall()]
                print(f"\n📋 Available tables in schema '{current_schema}' ({len(tables)}):")
                for table, table_type in tables:
                    print(f"   - {table} ({table_type})")
                
                # Test a simple query on the users table
                if 'users' in [t[0] for t in tables]:
                    logger.info("Testing query on 'users' table...")
                    try:
                        result = connection.execute(text("SELECT COUNT(*) FROM users"))
                        user_count = result.scalar()
                        print(f"\n👥 Found {user_count} users in the database")
                    except Exception as e:
                        logger.error(f"Error querying users table: {e}")
                
                return True
                
        except exc.OperationalError as oe:
            logger.error(f"Operational Error: {oe}")
            logger.error("This usually indicates a connection issue (wrong credentials, host unreachable, etc.)")
            return False
        except exc.ProgrammingError as pe:
            logger.error(f"Programming Error: {pe}")
            logger.error("This usually indicates an SQL syntax error or permission issue")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.error("Please check the logs for more details")
            return False
            
    except Exception as e:
        logger.critical(f"Critical error in test_connection: {e}", exc_info=True)
        print(f"\n❌ Critical error occurred. Please check the log file 'db_test.log' for details.")
        return False

if __name__ == "__main__":
    print("🔍 Testing database connection with detailed logging...")
    print(f"Log file: {os.path.abspath('db_test.log')}\n")
    
    success = test_connection()
    
    if success:
        print("\n✅ Database connection test completed successfully!")
    else:
        print("\n❌ Database connection test failed. Please check the log file for details.")
    
    print(f"\nLog file: {os.path.abspath('db_test.log')}")
