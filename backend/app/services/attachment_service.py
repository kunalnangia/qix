import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, UploadFile
from app.models.db_models import Attachment, TestCase
from app.schemas.attachment import AttachmentCreate

logger = logging.getLogger(__name__)


class AttachmentService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_attachment(
        self, file: UploadFile, test_case_id: str, user_id: str
    ) -> Attachment:
        test_case = await self.db.get(TestCase, test_case_id)
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {test_case_id} not found",
            )

        # In a real application, you would upload the file to a cloud storage
        # provider like S3 and store the URL in the database.
        # For this refactoring, we'll just store the filename.
        file_path = f"uploads/{uuid.uuid4()}_{file.filename}"

        db_attachment = Attachment(
            id=str(uuid.uuid4()),
            file_name=file.filename,
            file_path=file_path,
            file_type=file.content_type,
            test_case_id=test_case_id,
            uploaded_by=user_id,
        )
        self.db.add(db_attachment)
        await self.db.commit()
        await self.db.refresh(db_attachment)
        return db_attachment

    async def get_attachments_for_test_case(
        self, test_case_id: str
    ) -> List[Attachment]:
        stmt = select(Attachment).where(Attachment.test_case_id == test_case_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_attachment(self, attachment_id: str) -> Attachment:
        attachment = await self.db.get(Attachment, attachment_id)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found",
            )
        return attachment

    async def delete_attachment(self, attachment_id: str, user_id: str):
        attachment = await self.get_attachment(attachment_id)
        if attachment.uploaded_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this attachment",
            )

        # In a real application, you would also delete the file from cloud storage.
        await self.db.delete(attachment)
        await self.db.commit()
        return None
