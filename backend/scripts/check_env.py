import os
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    print(f"Loading environment from: {env_path}")
    
    load_dotenv(env_path, override=True)
    
    # Check if DATABASE_URL is set
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL is not set in the environment variables.")
        print("Please make sure you have a .env file with DATABASE_URL set.")
        return
    
    print("\nEnvironment variables:")
    print(f"DATABASE_URL: {'*' * 20 + db_url[-10:] if db_url else 'Not set'}")
    
    # Check if the database URL is using the correct format
    if "asyncpg" in db_url:
        print("\nWARNING: DATABASE_URL is using 'asyncpg' driver. For seeding, we need 'psycopg2'.")
        sync_url = db_url.replace("asyncpg", "psycopg2")
        print(f"Try using: {sync_url[:50]}...{sync_url[-20:]}")
    
    # Check if psycopg2 is installed
    try:
        import psycopg2
        print("\npsycopg2 is installed.")
    except ImportError:
        print("\nERROR: psycopg2 is not installed. Please install it with:")
        print("pip install psycopg2-binary")

if __name__ == "__main__":
    main()
