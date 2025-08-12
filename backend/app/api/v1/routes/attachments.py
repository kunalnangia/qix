from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.attachment import Attachment as AttachmentSchema
from app.core.security import get_current_user
from app.services.attachment_service import AttachmentService

router = APIRouter()


def get_attachment_service(db: AsyncSession = Depends(get_db)) -> AttachmentService:
    return AttachmentService(db)


@router.post("/", response_model=AttachmentSchema, status_code=status.HTTP_201_CREATED)
async def create_attachment(
    test_case_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    """
    Create a new attachment.
    """
    return await attachment_service.create_attachment(
        file=file, test_case_id=test_case_id, user_id=current_user["id"]
    )


@router.get("/test-case/{test_case_id}", response_model=List[AttachmentSchema])
async def get_attachments_for_test_case(
    test_case_id: str,
    current_user: dict = Depends(get_current_user),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    """
    Get all attachments for a test case.
    """
    return await attachment_service.get_attachments_for_test_case(
        test_case_id=test_case_id
    )


@router.get("/{attachment_id}", response_model=AttachmentSchema)
async def get_attachment(
    attachment_id: str,
    current_user: dict = Depends(get_current_user),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    """
    Get an attachment by ID.
    """
    return await attachment_service.get_attachment(attachment_id=attachment_id)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    current_user: dict = Depends(get_current_user),
    attachment_service: AttachmentService = Depends(get_attachment_service),
):
    """
    Delete an attachment.
    """
    await attachment_service.delete_attachment(
        attachment_id=attachment_id, user_id=current_user["id"]
    )
    return None
