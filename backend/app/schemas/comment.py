from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class CommentType(str, Enum):
    GENERAL = "general"
    ISSUE = "issue"
    SUGGESTION = "suggestion"
    QUESTION = "question"

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    comment_type: CommentType = CommentType.GENERAL

class CommentCreate(CommentBase):
    test_case_id: str

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    comment_type: Optional[CommentType] = None
    resolved: Optional[bool] = None

class CommentInDBBase(CommentBase):
    id: str
    test_case_id: str
    user_id: str
    user_name: str
    created_at: datetime
    updated_at: datetime
    resolved: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class Comment(CommentInDBBase):
    pass

class CommentInDB(CommentInDBBase):
    pass
