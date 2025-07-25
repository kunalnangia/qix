from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TESTER = "tester"
    DEVELOPER = "developer"
    MANAGER = "manager"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.TESTER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=8, max_length=50)

class UserInDBBase(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class User(UserInDBBase):
    pass

# Properties stored in DB (includes hashed password)
class UserInDB(UserInDBBase):
    hashed_password: str

# For JWT token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
