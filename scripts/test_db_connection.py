import sys
import os
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database configuration
import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# Import database configuration
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    from database.database_postgres import engine, Base
except ImportError:
    print("Error: Could not import database configuration. Make sure you're in the project root directory.")
    sys.exit(1)

def test_connection():
    try:
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            db_version = result.scalar()
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"Database version: {db_version}")
            
        # Test if we can create tables
        print("\nCreating tables...")
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error connecting to the database: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if the database server is running")
        print("2. Verify the database URL in .env file is correct")
        print("3. Ensure the database exists and the user has proper permissions")
        print(f"4. Check if you can connect using psql: psql {os.getenv('DATABASE_URL')}")
        return False
    
    return True

if __name__ == "__main__":
    test_connection()
