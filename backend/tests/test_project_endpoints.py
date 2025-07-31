import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.models.db_models import Project, User
from app.core.security import create_access_token
from datetime import datetime, timedelta

# Test data
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword",
    "full_name": "Test User"
}

TEST_PROJECT = {
    "name": "Test Project",
    "description": "Test project description",
    "is_active": True
}

@pytest.fixture
def test_user(db: Session):
    user = User(
        email=TEST_USER["email"],
        hashed_password=TEST_USER["password"],
        full_name=TEST_USER["full_name"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_project(db: Session, test_user):
    project = Project(
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
        is_active=TEST_PROJECT["is_active"],
        created_by=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@pytest.fixture
def client(db):
    # Override get_db dependency for testing
    def override_get_db():
        try:
            yield db
        finally:
            db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

def test_create_project(client, auth_headers):
    response = client.post(
        "/api/v1/projects",
        json=TEST_PROJECT,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == TEST_PROJECT["name"]
    assert data["description"] == TEST_PROJECT["description"]
    assert data["is_active"] == TEST_PROJECT["is_active"]

def test_get_project(client, test_project, auth_headers):
    response = client.get(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_project.id)
    assert data["name"] == test_project.name

def test_update_project(client, test_project, auth_headers):
    update_data = {"name": "Updated Project Name", "is_active": False}
    response = client.put(
        f"/api/v1/projects/{test_project.id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["is_active"] == update_data["is_active"]

def test_delete_project(client, test_project, auth_headers):
    response = client.delete(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify the project is deleted
    response = client.get(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers
    )
    assert response.status_code == 404

def test_list_projects(client, test_project, auth_headers):
    response = client.get(
        "/api/v1/projects",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(p["id"] == str(test_project.id) for p in data)
