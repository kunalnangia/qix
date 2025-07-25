"""Minimal FastAPI test with in-memory SQLite database."""
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import using absolute path
from backend.server import app
from backend.database_sqlite import Base

# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create all tables
Base.metadata.create_all(bind=test_engine)

# Override the database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[app.dependency_overrides.get('get_db')] = override_get_db

# Create a test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    print("\n=== Testing health check endpoint ===")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✓ Health check passed")

if __name__ == "__main__":
    print("Running minimal FastAPI test...")
    test_health_check()
    print("\nTest completed!")
