"""
Final database connection test script.
This script verifies that we can connect to the database using the .env configuration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def load_environment():
    """Load environment variables from .env file."""
    # Get the path to the .env file
    env_path = Path(__file__).parent.parent / '.env'
    
    # Load environment variables
    if not env_path.exists():
        print(f"[ERROR] .env file not found at: {env_path}")
        return False
    
    print(f"[INFO] Loading environment from: {env_path}")
    load_dotenv(dotenv_path=env_path, override=True)
    return True

def get_database_url():
    """Get the database URL from environment variables."""
    # Get the database URL from environment variables
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("[ERROR] DATABASE_URL not found in environment variables")
        return None
    
    # Convert postgres:// to postgresql:// if needed
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def test_database_connection(db_url):
    """Test the database connection."""
    print("\n=== Testing Database Connection ===")
    
    try:
        # Parse the database URL
        import urllib.parse
        result = urllib.parse.urlparse(db_url)
        
        # Extract connection parameters
        dbname = result.path[1:]  # Remove the leading '/'
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432
        
        print(f"Connecting to database: {user}@{host}:{port}/{dbname}")
        
        # Connect to the database
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # Set isolation level to autocommit for certain operations
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        with conn.cursor() as cur:
            # Get database version
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            print(f"\n[SUCCESS] Connected to database")
            print(f"Database version: {db_version[0]}")
            
            # List all tables in the public schema
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = cur.fetchall()
            print(f"\nFound {len(tables)} tables in the public schema:")
            for i, (table_name,) in enumerate(tables, 1):
                print(f"  {i}. {table_name}")
            
            # If there are tables, show the first few rows of the first table
            if tables:
                table_name = tables[0][0]
                print(f"\nFirst few rows of table '{table_name}':")
                
                try:
                    cur.execute(sql.SQL("SELECT * FROM {table} LIMIT 3").format(
                        table=sql.Identifier(table_name)
                    ))
                    
                    # Get column names
                    colnames = [desc[0] for desc in cur.description]
                    print("  " + " | ".join(colnames))
                    print("  " + "-" * (sum(len(c) for c in colnames) + 3 * (len(colnames) - 1)))
                    
                    # Get rows
                    for row in cur.fetchall():
                        print("  " + " | ".join(str(value) for value in row))
                except Exception as e:
                    print(f"  [WARNING] Could not read from table '{table_name}': {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function."""
    print("=== Database Connection Test ===")
    
    # Load environment variables
    if not load_environment():
        return 1
    
    # Get database URL
    db_url = get_database_url()
    if not db_url:
        return 1
    
    # Mask the password in the URL for security
    import re
    masked_url = re.sub(r':[^@]+@', ':***@', db_url)
    print(f"Using database URL: {masked_url}")
    
    # Test the database connection
    success = test_database_connection(db_url)
    
    if success:
        print("\n[SUCCESS] Database connection test completed successfully!")
        return 0
    else:
        print("\n[ERROR] Database connection test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
