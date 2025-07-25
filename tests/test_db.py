"""Test database functionality in isolation."""
import sys
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database module
from backend.database_sqlite import Base, engine, SessionLocal

# Test database URL
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

def test_database_connection():
    """Test database connection and table creation."""
    print("\n=== Testing database connection ===")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Test connection
    try:
        db = SessionLocal()
        # Use text() for raw SQL expressions
        db.execute(text("SELECT 1"))
        print("✓ Database connection successful")
        db.close()
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    print("Running database tests...")
    test_database_connection()
    print("\nAll database tests completed!")
