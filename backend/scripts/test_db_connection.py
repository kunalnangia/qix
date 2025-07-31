import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SQLALCHEMY_DATABASE_URL

def test_connection():
    print("Testing database connection...")
    print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
    
    try:
        # Create a synchronous engine for testing
        sync_engine = create_engine(
            str(SQLALCHEMY_DATABASE_URL).replace("asyncpg", "psycopg2"),
            echo=True
        )
        
        # Test the connection
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"\nSuccessfully connected to database!")
            print(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            tables = [row[0] for row in result.fetchall()]
            print("\nTables in the database:")
            for table in sorted(tables):
                print(f"- {table}")
                
    except Exception as e:
        print(f"\nError connecting to database: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
    
    test_connection()
