import logging
import uuid
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.db_models import Comment, TestCase
from app.schemas.comment import CommentCreate

logger = logging.getLogger(__name__)


class CommentService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_comment(self, comment_data: CommentCreate, user_id: str, user_name: str) -> Comment:
        test_case = await self.db.get(TestCase, comment_data.test_case_id)
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {comment_data.test_case_id} not found",
            )

        db_comment = Comment(
            **comment_data.dict(),
            id=str(uuid.uuid4()),
            user_id=user_id,
            user_name=user_name,
        )
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment

    async def get_comments_for_test_case(self, test_case_id: str) -> List[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.test_case_id == test_case_id)
            .order_by(Comment.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def resolve_comment(self, comment_id: str, user_id: str) -> Comment:
        db_comment = await self.db.get(Comment, comment_id)
        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )

        if db_comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to resolve this comment",
            )

        db_comment.resolved = True
        db_comment.resolved_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment
