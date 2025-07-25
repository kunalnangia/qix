from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class EnvironmentBase(BaseModel):
    """Base schema for Environment"""
    name: str
    description: Optional[str] = None
    project_id: str
    base_url: str
    is_active: bool = True
    variables: Dict[str, Any] = {}
    headers: Dict[str, str] = {}
    auth: Optional[Dict[str, Any]] = None

class EnvironmentCreate(EnvironmentBase):
    """Schema for creating a new environment"""
    pass

class EnvironmentUpdate(BaseModel):
    """Schema for updating an environment"""
    name: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None
    variables: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    auth: Optional[Dict[str, Any]] = None

class Environment(EnvironmentBase):
    """Complete Environment schema with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
