"""Test with absolute imports from the project root."""
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now import using the full path
print(f"\n=== Testing absolute imports from: {project_root} ===")

try:
    from backend.database_sqlite import Base, engine, SessionLocal
    print("✓ Successfully imported database components")
    
    # Test database connection
    from sqlalchemy import text
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
        print("✓ Database connection successful")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    raise

print("\nAll tests completed successfully!")
