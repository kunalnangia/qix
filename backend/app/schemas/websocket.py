from pydantic import BaseModel, Field, validator, HttpUrl, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey

class TestType(str, Enum):
    FUNCTIONAL = "functional"
    API = "api"
    VISUAL = "visual"
    PERFORMANCE = "performance"
    SECURITY = "security"
    INTEGRATION = "integration"
    UNIT = "unit"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CommentType(str, Enum):
    GENERAL = "general"
    ISSUE = "issue"
    SUGGESTION = "suggestion"
    RESOLVED = "resolved"

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    role: str = "tester"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Project Models
class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_by: str
    team_members: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

# Test Case Models
class TestStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int
    description: str
    expected_result: str
    actual_result: Optional[str] = None
    status: Optional[str] = None
    test_case_id: str = Field(..., description="UUID of the parent test case")

class TestCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    project_id: str
    test_type: TestType
    priority: Priority
    status: Status
    steps: List[TestStep] = []
    expected_result: Optional[str] = None
    created_by: str
    assigned_to: Optional[str] = None
    tags: List[str] = []
    ai_generated: bool = False
    self_healing_enabled: bool = False
    prerequisites: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    automation_config: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TestCaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    test_type: TestType
    priority: Priority
    status: Status = Status.DRAFT
    steps: List[TestStep] = []
    expected_result: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = []
    ai_generated: bool = False
    self_healing_enabled: bool = False
    prerequisites: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    automation_config: Optional[Dict[str, Any]] = None

class TestCaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[TestType] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    steps: Optional[List[TestStep]] = None
    expected_result: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    self_healing_enabled: Optional[bool] = None
    prerequisites: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    automation_config: Optional[Dict[str, Any]] = None

# Test Plan Models
class TestPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    project_id: str
    test_cases: List[str] = []
    created_by: str
    status: Status = Status.DRAFT
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TestPlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: str
    test_cases: List[str] = []
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

# Test Execution Models
class TestExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_case_id: str
    test_plan_id: Optional[str] = None
    executed_by: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None  # in seconds
    result: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None
    screenshots: List[str] = []
    error_message: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TestExecutionCreate(BaseModel):
    test_case_id: str
    test_plan_id: Optional[str] = None

# Comment Models
class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_case_id: str
    user_id: str
    user_name: str
    comment_type: CommentType = CommentType.GENERAL
    content: str
    parent_comment_id: Optional[str] = None
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CommentCreate(BaseModel):
    test_case_id: str
    comment_type: CommentType = CommentType.GENERAL
    content: str
    parent_comment_id: Optional[str] = None

# AI Models
class AITestGenerationRequest(BaseModel):
    project_id: str
    prompt: str
    test_type: TestType
    priority: Priority = Priority.MEDIUM
    count: int = 1

class AIDebugRequest(BaseModel):
    test_case_id: str
    execution_id: str
    error_description: str
    logs: Optional[str] = None

class AIPrioritizationRequest(BaseModel):
    project_id: str
    context: str
    test_case_ids: List[str]

class AIAnalysisResult(BaseModel):
    success: bool
    analysis: str
    suggestions: List[str]
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Dashboard Models
class DashboardStats(BaseModel):
    total_test_cases: int
    total_executions: int
    pass_rate: float
    average_execution_time: float
    active_test_runs: int
    recent_activity: List[Dict[str, Any]]

class ActivityFeed(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    action: str
    target_type: str  # test_case, execution, comment, etc.
    target_id: str
    target_name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Team Models
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

class TeamDetail(Team):
    members: List[Dict[str, Any]] = []
    
    class Config:
        orm_mode = True

class TeamMemberBase(BaseModel):
    user_id: str
    role: str = "member"

class TeamMemberCreate(TeamMemberBase):
    team_id: str

class TeamMember(TeamMemberBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

# WebSocket Models
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NotificationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str
    title: str
    message: str
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)