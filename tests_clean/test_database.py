"""Test database module imports directly."""
import sys
import os
import importlib.util

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_database_import():
    """Test importing the database module."""
    print("\n=== Testing database import ===")
    
    # Try to import database_sqlite directly
    try:
        import backend.database_sqlite as db
        print("✓ Successfully imported backend.database_sqlite")
        print(f"   Location: {db.__file__}")
        
        # Check if we can access database objects
        print("\nDatabase objects:")
        print(f"- SQLALCHEMY_DATABASE_URL: {getattr(db, 'SQLALCHEMY_DATABASE_URL', 'Not found')}")
        print(f"- engine: {'Found' if hasattr(db, 'engine') else 'Not found'}")
        print(f"- SessionLocal: {'Found' if hasattr(db, 'SessionLocal') else 'Not found'}")
        print(f"- Base: {'Found' if hasattr(db, 'Base') else 'Not found'}")
        
        return True
    except Exception as e:
        print(f"✗ Error importing backend.database_sqlite: {e}")
        return False

def test_server_import():
    """Test importing the server module."""
    print("\n=== Testing server import ===")
    
    # First, ensure database_sqlite is in sys.modules
    try:
        import backend.database_sqlite as db
        print("✓ backend.database_sqlite is in sys.modules")
    except Exception as e:
        print(f"✗ Could not import backend.database_sqlite: {e}")
        return False
    
    # Now try to import server
    try:
        import backend.server
        print("✓ Successfully imported backend.server")
        print(f"   Location: {backend.server.__file__}")
        return True
    except Exception as e:
        print(f"✗ Error importing backend.server: {e}")
        return False

if __name__ == "__main__":
    print("Running database import tests...")
    test_database_import()
    test_server_import()
    print("\nTests completed!")
