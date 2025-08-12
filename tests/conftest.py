import os
import sys
from pathlib import Path
import pytest

# Add project root to the Python path to allow for absolute imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app

# Test database URL - using SQLite in-memory for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine and session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db

# Test client fixture
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

# Database session fixture
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# Test user data
@pytest.fixture(scope="module")
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

# Create test user in the database
@pytest.fixture(scope="function")
def create_test_user(db_session, test_user):
    from backend.models import User
    
    # Check if user already exists
    user = db_session.query(User).filter(User.email == test_user["email"]).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=test_user["email"],
            hashed_password=test_user["password"],  # In a real app, this should be hashed
            full_name=test_user["full_name"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    
    return user

# Authentication header fixture
@pytest.fixture(scope="function")
def auth_headers(client, test_user, create_test_user):
    # In a real app, you would get a token from your auth endpoint
    # For testing, we'll use a mock token or basic auth
    return {"Authorization": f"Bearer test_token"}
