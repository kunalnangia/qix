import pytest
from fastapi import status
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from backend import models, schemas

def test_create_environment(client, db_session: Session, auth_headers, create_test_user):
    """Test creating a new environment"""
    # First, create a test project
    project = models.Project(
        id=str(uuid.uuid4()),
        name="Test Project",
        description="A test project",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(project)
    db_session.commit()
    
    environment_data = {
        "name": "Test Environment",
        "description": "A test environment",
        "base_url": "https://test.example.com",
        "project_id": str(project.id),
        "is_active": True,
        "variables": {"key1": "value1", "key2": "value2"}
    }
    
    response = client.post(
        "/environments/",
        json=environment_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["name"] == environment_data["name"]
    assert data["description"] == environment_data["description"]
    assert data["base_url"] == environment_data["base_url"]
    assert data["project_id"] == environment_data["project_id"]
    assert data["is_active"] == environment_data["is_active"]
    assert data["variables"] == environment_data["variables"]
    assert "id" in data
    
    # Verify environment was created in the database
    environment = db_session.query(models.Environment).filter(
        models.Environment.id == data["id"]
    ).first()
    
    assert environment is not None
    assert environment.name == environment_data["name"]

def test_list_environments(client, db_session: Session, auth_headers, create_test_user):
    """Test listing environments for a project"""
    # Create a test project
    project = models.Project(
        id=str(uuid.uuid4()),
        name="Test Project",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(project)
    
    # Create test environments
    env1 = models.Environment(
        id=str(uuid.uuid4()),
        name="Test Env 1",
        base_url="https://test1.example.com",
        project_id=project.id,
        is_active=True,
        variables={"key1": "value1"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    env2 = models.Environment(
        id=str(uuid.uuid4()),
        name="Test Env 2",
        base_url="https://test2.example.com",
        project_id=project.id,
        is_active=False,
        variables={"key2": "value2"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db_session.add_all([env1, env2])
    db_session.commit()
    
    # Test listing active environments only
    response = client.get(
        f"/environments/project/{project.id}",
        params={"active_only": True},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Test Env 1"
    
    # Test listing all environments
    response = client.get(
        f"/environments/project/{project.id}",
        params={"active_only": False},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 2
    assert any(env["name"] == "Test Env 1" for env in data)
    assert any(env["name"] == "Test Env 2" for env in data)

def test_update_environment(client, db_session: Session, auth_headers, create_test_user):
    """Test updating an environment"""
    # Create a test project
    project = models.Project(
        id=str(uuid.uuid4()),
        name="Test Project",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(project)
    
    # Create a test environment
    environment = models.Environment(
        id=str(uuid.uuid4()),
        name="Old Name",
        description="Old description",
        base_url="https://old.example.com",
        project_id=project.id,
        is_active=True,
        variables={"old_key": "old_value"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(environment)
    db_session.commit()
    
    # Update the environment
    update_data = {
        "name": "New Name",
        "description": "New description",
        "base_url": "https://new.example.com",
        "is_active": False,
        "variables": {"new_key": "new_value"}
    }
    
    response = client.put(
        f"/environments/{environment.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["base_url"] == update_data["base_url"]
    assert data["is_active"] == update_data["is_active"]
    assert data["variables"] == update_data["variables"]
    
    # Verify the environment was updated in the database
    updated_env = db_session.query(models.Environment).filter(
        models.Environment.id == environment.id
    ).first()
    
    assert updated_env.name == update_data["name"]
    assert updated_env.description == update_data["description"]
    assert updated_env.base_url == update_data["base_url"]
    assert updated_env.is_active == update_data["is_active"]
    assert updated_env.variables == update_data["variables"]

def test_delete_environment(client, db_session: Session, auth_headers, create_test_user):
    """Test deleting an environment"""
    # Create a test project
    project = models.Project(
        id=str(uuid.uuid4()),
        name="Test Project",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(project)
    
    # Create a test environment
    environment = models.Environment(
        id=str(uuid.uuid4()),
        name="Test Environment",
        base_url="https://test.example.com",
        project_id=project.id,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(environment)
    db_session.commit()
    
    # Delete the environment
    response = client.delete(
        f"/environments/{environment.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the environment was deleted from the database
    deleted_env = db_session.query(models.Environment).filter(
        models.Environment.id == environment.id
    ).first()
    
    assert deleted_env is None
    
    # Test deleting a non-existent environment
    response = client.delete(
        f"/environments/{uuid.uuid4()}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
