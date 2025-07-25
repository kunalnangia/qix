import os
import shutil
import uuid
import mimetypes
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

# Import from app modules
from app import schemas
from app.models import db_models as models
from app.db.session import get_db
from app.auth.security import get_current_user
from app.core.config import settings

router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
    responses={404: {"description": "Not found"}},
)

def get_upload_dir() -> str:
    """Get the upload directory, create if it doesn't exist"""
    upload_dir = os.path.join(settings.BASE_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@router.post("/upload", response_model=schemas.Attachment, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file attachment
    """
    # Validate entity type
    if entity_type not in ["test_case", "test_execution", "test_plan"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entity_type. Must be one of: test_case, test_execution, test_plan"
        )
    
    # Check if entity exists and user has access
    if entity_type == "test_case":
        entity = db.query(models.TestCase).filter(models.TestCase.id == entity_id).first()
    elif entity_type == "test_execution":
        entity = db.query(models.TestExecution).filter(models.TestExecution.id == entity_id).first()
    elif entity_type == "test_plan":
        entity = db.query(models.TestPlan).filter(models.TestPlan.id == entity_id).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.replace('_', ' ').title()} not found"
        )
    
    # Generate a unique filename
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}{file_ext}"
    
    # Create upload directory if it doesn't exist
    upload_dir = get_upload_dir()
    file_path = os.path.join(upload_dir, file_name)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    
    # Create attachment record
    db_attachment = models.Attachment(
        id=file_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        entity_type=entity_type,
        entity_id=entity_id,
        uploaded_by=current_user["id"],
        description=description,
        created_at=datetime.utcnow()
    )
    
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    
    return db_attachment

@router.get("/{entity_type}/{entity_id}", response_model=List[schemas.Attachment])
async def list_attachments(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all attachments for an entity
    """
    # Validate entity type
    if entity_type not in ["test_case", "test_execution", "test_plan"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entity_type. Must be one of: test_case, test_execution, test_plan"
        )
    
    # Check if user has access to the entity
    if entity_type == "test_case":
        entity = db.query(models.TestCase).filter(models.TestCase.id == entity_id).first()
    elif entity_type == "test_execution":
        entity = db.query(models.TestExecution).filter(models.TestExecution.id == entity_id).first()
    elif entity_type == "test_plan":
        entity = db.query(models.TestPlan).filter(models.TestPlan.id == entity_id).first()
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.replace('_', ' ').title()} not found"
        )
    
    # Get attachments
    attachments = db.query(models.Attachment).filter(
        models.Attachment.entity_type == entity_type,
        models.Attachment.entity_id == entity_id
    ).all()
    
    return attachments

@router.get("/download/{attachment_id}")
async def download_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Download an attachment
    """
    attachment = db.query(models.Attachment).filter(
        models.Attachment.id == attachment_id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Check if file exists
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Return file as a streaming response
    from fastapi.responses import FileResponse
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.file_name,
        media_type=attachment.file_type
    )

@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an attachment
    """
    attachment = db.query(models.Attachment).filter(
        models.Attachment.id == attachment_id,
        models.Attachment.uploaded_by == current_user["id"]  # Only allow uploader to delete
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found or you don't have permission to delete it"
        )
    
    # Delete file
    try:
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
    except Exception as e:
        # Log error but continue with DB deletion
        print(f"Error deleting file: {str(e)}")
    
    # Delete attachment record
    db.delete(attachment)
    db.commit()
    
    return None
