from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

class TokenData(BaseModel):
    """Schema for token data payload"""
    email: Optional[str] = None
    user_id: Optional[str] = None
    exp: Optional[int] = None
    
class TokenCreate(BaseModel):
    """Schema for token creation"""
    email: str
    password: str

class TokenVerify(BaseModel):
    """Schema for token verification"""
    token: str
