from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.db_models import Comment
from app.models.db_models import TestCase as DBTestCase
from app.models.db_models import User
from app.schemas.comment import CommentCreate, CommentInDB
from app.core.security import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentInDB, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a test case
    """
    # Verify test case exists
    test_case = db.query(TestCase).filter(TestCase.id == comment_in.test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {comment_in.test_case_id} not found"
        )
    
    comment = Comment(
        id=str(uuid.uuid4()),
        content=comment_in.content,
        test_case_id=comment_in.test_case_id,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment

@router.get("/test-case/{test_case_id}", response_model=List[CommentInDB])
def get_comments_for_test_case(
    test_case_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a test case
    """
    # Verify test case exists
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    comments = db.query(Comment).filter(
        Comment.test_case_id == test_case_id
    ).order_by(
        Comment.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return comments

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment (only allowed by comment author or admin)
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Only allow comment author or admin to delete
    if comment.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    db.delete(comment)
    db.commit()
    
    return None
