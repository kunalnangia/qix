from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID as PyUUID
from .user import User  # Assuming User schema exists

class AttachmentBase(BaseModel):
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    entity_type: str
    entity_id: str
    description: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    pass

class AttachmentUpdate(BaseModel):
    description: Optional[str] = None

class AttachmentInDBBase(AttachmentBase):
    id: str
    uploaded_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Properties to return to client
class Attachment(AttachmentInDBBase):
    uploader: Optional[User] = None

# Properties stored in DB
class AttachmentInDB(AttachmentInDBBase):
    pass
