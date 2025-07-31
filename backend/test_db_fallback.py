import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_sqlite():
    try:
        # Test SQLite connection
        db_url = "sqlite:///./test.db"
        print(f"🔍 Testing SQLite connection to: {db_url}")
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            print(f"✅ Connected to SQLite version: {version}")
            return True
    except Exception as e:
        print(f"❌ SQLite connection failed: {str(e)}")
        return False

def test_postgresql():
    try:
        # Test PostgreSQL connection
        db_url = "postgresql://postgres:postgres@localhost:5432/intellitest"
        print(f"\n🔍 Testing PostgreSQL connection to: {db_url}")
        engine = create_engine(db_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {str(e)}")
        print("\nTroubleshooting steps for PostgreSQL:")
        print("1. Make sure PostgreSQL is installed and running")
        print("2. Create the database: createdb intellitest")
        print("3. Check your credentials in .env file")
        return False

def main():
    print("🔧 Testing database connections...")
    
    # First try SQLite
    if test_sqlite():
        print("\n✅ SQLite is working! You can use SQLite for development.")
        print("   To use SQLite, update your .env file with:")
        print("   DATABASE_URL=sqlite:///./test.db")
        return
        
    # If SQLite fails, try PostgreSQL
    if test_postgresql():
        print("\n✅ PostgreSQL is working!")
        return
        
    print("\n❌ Could not connect to any database.")
    print("Please install either SQLite (built into Python) or PostgreSQL.")
    print("For development, SQLite is recommended for simplicity.")

if __name__ == "__main__":
    main()
