import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.resolve())
sys.path.insert(0, project_root)

from sqlalchemy import text
from backend.database.config import engine, get_db_session

def test_db_connection():
    print("Testing database connection...")
    try:
        with get_db_session() as db:
            # Simple query to test the connection
            result = db.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting database connection test...")
    success = test_db_connection()
    sys.exit(0 if success else 1)
