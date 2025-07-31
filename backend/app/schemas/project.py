from pydantic import BaseModel, Field, ConfigDict, UUID4
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from app.models.db_models import Status as DBStatus

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ProjectBase(BaseModel):
    """Base schema for Project data validation"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the project")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the project")
    team_id: Optional[str] = Field(None, description="ID of the team this project belongs to")
    is_active: bool = Field(default=True, description="Whether the project is active")

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass

class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the project")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the project")
    team_id: Optional[str] = Field(None, description="ID of the team this project belongs to")
    is_active: Optional[bool] = Field(None, description="Whether the project is active")

class ProjectInDBBase(ProjectBase):
    """Base schema for Project data stored in DB"""
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Project(ProjectInDBBase):
    """Schema for returning project data to client"""
    test_case_count: Optional[int] = Field(None, description="Number of test cases in this project")
    environment_count: Optional[int] = Field(None, description="Number of environments configured for this project")
    last_execution: Optional[datetime] = Field(None, description="Timestamp of the last test execution")

class ProjectInDB(ProjectInDBBase):
    """Schema for project data stored in database"""
    pass

class ProjectStats(BaseModel):
    """Schema for project statistics"""
    total_test_cases: int = 0
    active_test_cases: int = 0
    test_cases_by_status: Dict[str, int] = {}
    test_cases_by_priority: Dict[str, int] = {}
    test_executions: Dict[str, int] = {}
    last_updated: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)