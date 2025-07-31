from pydantic import BaseModel, EmailStr, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)  # Fixed Pydantic v2 config

# Properties to return to client
class User(UserInDBBase):
    pass

# Properties stored in DB (includes hashed password)
class UserInDB(UserInDBBase):
    hashed_password: str

class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "your_password"
            }
        }
    )

# For JWT token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
