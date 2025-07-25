import os
import io
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

from backend import models, schemas

# Test file data for upload
TEST_FILE_CONTENT = b"This is a test file content"
TEST_FILE_NAME = "test_file.txt"

@pytest.fixture
def test_file():
    return ("test_file.txt", io.BytesIO(TEST_FILE_CONTENT), "text/plain")

def test_upload_attachment(client: TestClient, db_session: Session, auth_headers, create_test_user, test_file):
    """Test uploading a file attachment"""
    # Create a test test case
    test_case = models.TestCase(
        id=str(uuid.uuid4()),
        title="Test Case",
        project_id=str(uuid.uuid4()),
        test_type="functional",
        priority="medium",
        status="draft",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(test_case)
    db_session.commit()
    
    # Mock file upload
    files = {"file": (TEST_FILE_NAME, TEST_FILE_CONTENT, "text/plain")}
    data = {
        "entity_type": "test_case",
        "entity_id": str(test_case.id),
        "description": "Test attachment"
    }
    
    with patch("os.makedirs"), \
         patch("shutil.copyfileobj"), \
         patch("os.path.getsize", return_value=len(TEST_FILE_CONTENT)):
        
        response = client.post(
            "/attachments/upload",
            data=data,
            files=files,
            headers=auth_headers
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    assert data["file_name"] == TEST_FILE_NAME
    assert data["entity_type"] == "test_case"
    assert data["entity_id"] == str(test_case.id)
    assert data["description"] == "Test attachment"
    assert data["file_size"] == len(TEST_FILE_CONTENT)
    assert "id" in data
    
    # Verify attachment was created in the database
    attachment = db_session.query(models.Attachment).filter(
        models.Attachment.id == data["id"]
    ).first()
    
    assert attachment is not None
    assert attachment.file_name == TEST_FILE_NAME

def test_list_attachments(client: TestClient, db_session: Session, auth_headers, create_test_user):
    """Test listing attachments for an entity"""
    # Create a test test case
    test_case = models.TestCase(
        id=str(uuid.uuid4()),
        title="Test Case",
        project_id=str(uuid.uuid4()),
        test_type="functional",
        priority="medium",
        status="draft",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(test_case)
    
    # Create test attachments
    attachment1 = models.Attachment(
        id=str(uuid.uuid4()),
        file_name="file1.txt",
        file_path="/path/to/file1.txt",
        file_size=1024,
        file_type="text/plain",
        entity_type="test_case",
        entity_id=test_case.id,
        uploaded_by=create_test_user.id,
        description="First attachment",
        created_at=datetime.utcnow()
    )
    
    attachment2 = models.Attachment(
        id=str(uuid.uuid4()),
        file_name="file2.jpg",
        file_path="/path/to/file2.jpg",
        file_size=2048,
        file_type="image/jpeg",
        entity_type="test_case",
        entity_id=test_case.id,
        uploaded_by=create_test_user.id,
        description="Second attachment",
        created_at=datetime.utcnow()
    )
    
    db_session.add_all([test_case, attachment1, attachment2])
    db_session.commit()
    
    # Test listing attachments
    response = client.get(
        f"/attachments/test_case/{test_case.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 2
    assert any(att["file_name"] == "file1.txt" for att in data)
    assert any(att["file_name"] == "file2.jpg" for att in data)

def test_download_attachment(client: TestClient, db_session: Session, auth_headers, create_test_user, tmp_path):
    """Test downloading an attachment"""
    # Create a test test case
    test_case = models.TestCase(
        id=str(uuid.uuid4()),
        title="Test Case",
        project_id=str(uuid.uuid4()),
        test_type="functional",
        priority="medium",
        status="draft",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(test_case)
    
    # Create a test file
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test file content")
    
    # Create a test attachment
    attachment = models.Attachment(
        id=str(uuid.uuid4()),
        file_name="test_file.txt",
        file_path=str(file_path),
        file_size=len("Test file content"),
        file_type="text/plain",
        entity_type="test_case",
        entity_id=test_case.id,
        uploaded_by=create_test_user.id,
        description="Test attachment",
        created_at=datetime.utcnow()
    )
    
    db_session.add_all([test_case, attachment])
    db_session.commit()
    
    # Test downloading the attachment
    response = client.get(
        f"/attachments/download/{attachment.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/plain"
    assert "content-disposition" in response.headers
    assert "test_file.txt" in response.headers["content-disposition"]
    assert response.content == b"Test file content"

def test_delete_attachment(client: TestClient, db_session: Session, auth_headers, create_test_user, tmp_path):
    """Test deleting an attachment"""
    # Create a test test case
    test_case = models.TestCase(
        id=str(uuid.uuid4()),
        title="Test Case",
        project_id=str(uuid.uuid4()),
        test_type="functional",
        priority="medium",
        status="draft",
        created_by=create_test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(test_case)
    
    # Create a test file
    file_path = tmp_path / "test_file_to_delete.txt"
    file_path.write_text("Test file content")
    
    # Create a test attachment
    attachment = models.Attachment(
        id=str(uuid.uuid4()),
        file_name="test_file_to_delete.txt",
        file_path=str(file_path),
        file_size=len("Test file content"),
        file_type="text/plain",
        entity_type="test_case",
        entity_id=test_case.id,
        uploaded_by=create_test_user.id,
        description="Test attachment to delete",
        created_at=datetime.utcnow()
    )
    
    db_session.add_all([test_case, attachment])
    db_session.commit()
    
    # Test deleting the attachment
    response = client.delete(
        f"/attachments/{attachment.id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the attachment was deleted from the database
    deleted_attachment = db_session.query(models.Attachment).filter(
        models.Attachment.id == attachment.id
    ).first()
    
    assert deleted_attachment is None
    
    # Verify the file was deleted
    assert not os.path.exists(file_path)
    
    # Test deleting a non-existent attachment
    response = client.delete(
        f"/attachments/{uuid.uuid4()}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
