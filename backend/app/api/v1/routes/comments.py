from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.comment import CommentCreate, Comment as CommentSchema
from app.core.security import get_current_user
from app.services.comment_service import CommentService
from app.websocket.manager import websocket_manager

router = APIRouter()


def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(db)


@router.post("/", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_in: CommentCreate,
    current_user: dict = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    """
    Create a new comment.
    """
    comment = await comment_service.create_comment(
        comment_data=comment_in,
        user_id=current_user["id"],
        user_name=current_user["full_name"],
    )
    await websocket_manager.broadcast_comment_update(comment.dict())
    return comment


@router.get("/{test_case_id}", response_model=List[CommentSchema])
async def get_comments(
    test_case_id: str,
    current_user: dict = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    """
    Get comments for a test case.
    """
    return await comment_service.get_comments_for_test_case(test_case_id=test_case_id)


@router.put("/{comment_id}/resolve", response_model=CommentSchema)
async def resolve_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
):
    """
    Resolve a comment.
    """
    comment = await comment_service.resolve_comment(
        comment_id=comment_id, user_id=current_user["id"]
    )
    await websocket_manager.broadcast_comment_update(comment.dict())
    return comment
