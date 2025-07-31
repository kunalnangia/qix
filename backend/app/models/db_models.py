from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
import uuid

# Import Base from app.db.base to avoid circular imports
from app.db.base import Base

# Enums
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


# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="tester")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_test_cases = relationship("TestCase", foreign_keys="[TestCase.created_by]", back_populates="creator")
    assigned_test_cases = relationship("TestCase", foreign_keys="[TestCase.assigned_to]", back_populates="assignee")
    activity_logs = relationship("ActivityLog", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    test_executions = relationship("TestExecution", back_populates="executor")
    created_projects = relationship("Project", back_populates="creator")
    team_memberships = relationship("TeamMember", back_populates="user")
    uploaded_attachments = relationship("Attachment", back_populates="uploader")

# Project Model
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="created_projects")
    team = relationship("Team", back_populates="projects")
    test_cases = relationship("TestCase", back_populates="project")
    test_plans = relationship("TestPlan", back_populates="project")
    environments = relationship("Environment", back_populates="project")

# Test Step Model (for TestCase)
class TestStep(Base):
    __tablename__ = "test_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = Column(String, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    
    # Relationship
    test_case = relationship("TestCase", back_populates="steps")

# Test Case Model
class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    test_type = Column(SQLEnum(TestType), nullable=False)
    priority = Column(SQLEnum(Priority), nullable=False)
    status = Column(SQLEnum(Status), nullable=False, default=Status.DRAFT)
    expected_result = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    tags = Column(JSON, default=list)
    ai_generated = Column(Boolean, default=False)
    self_healing_enabled = Column(Boolean, default=False)
    prerequisites = Column(Text, nullable=True)
    test_data = Column(JSON, nullable=True)
    automation_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="test_cases")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_test_cases")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_test_cases")
    steps = relationship("TestStep", back_populates="test_case", cascade="all, delete-orphan")
    test_executions = relationship("TestExecution", back_populates="test_case")
    comments = relationship("Comment", back_populates="test_case")
    test_plans = relationship("TestPlan", secondary="test_plan_test_cases", back_populates="test_cases")
    test_plan_test_cases = relationship("TestPlanTestCase", back_populates="test_case", cascade="all, delete-orphan")

# Test Plan Model
class TestPlan(Base):
    __tablename__ = "test_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(Status), default=Status.DRAFT)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="test_plans")
    test_executions = relationship("TestExecution", back_populates="test_plan")
    test_cases = relationship("TestCase", secondary="test_plan_test_cases", back_populates="test_plans")
    test_plan_test_cases = relationship("TestPlanTestCase", back_populates="test_plan", cascade="all, delete-orphan")



# Test Execution Model
class TestExecution(Base):
    __tablename__ = "test_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = Column(String, ForeignKey("test_cases.id"), nullable=False)
    test_plan_id = Column(String, ForeignKey("test_plans.id"), nullable=True)
    executed_by = Column(String, ForeignKey("users.id"), nullable=False)
    environment_id = Column(String, ForeignKey("environments.id"), nullable=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    result = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    screenshots = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="test_executions")
    test_plan = relationship("TestPlan", back_populates="test_executions")
    executor = relationship("User", back_populates="test_executions")
    environment = relationship("Environment", back_populates="test_executions")

# Comment Model
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = Column(String, ForeignKey("test_cases.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    comment_type = Column(SQLEnum(CommentType), default=CommentType.GENERAL)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(String, ForeignKey("comments.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent_comment = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent_comment", cascade="all, delete-orphan")


# Team Model
class Team(Base):
    __tablename__ = "teams"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("TeamMember", back_populates="team")
    projects = relationship("Project", back_populates="team")


# Team Member Model (for many-to-many relationship between User and Team)
class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # member, admin, owner
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


# Environment Model
class Environment(Base):
    __tablename__ = "environments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    base_url = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    variables = Column(JSON, default=dict)  # Environment variables
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="environments")
    test_executions = relationship("TestExecution", back_populates="environment")


# Attachment Model
class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # 'test_case', 'test_execution', etc.
    entity_id = Column(String, nullable=False)    # ID of the related entity
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_attachments")


# Test Plan Test Case Association Model
class TestPlanTestCase(Base):
    """Association table for many-to-many relationship between TestPlan and TestCase with additional attributes"""
    __tablename__ = 'test_plan_test_cases'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_plan_id = Column(String, ForeignKey('test_plans.id', ondelete='CASCADE'), nullable=False)
    test_case_id = Column(String, ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False)
    
    # Optional fields for the association
    order = Column(Integer, default=0)  # Order of test case in the test plan
    is_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey('users.id'))
    
    # Relationships
    test_plan = relationship("TestPlan", back_populates="test_plan_test_cases")
    test_case = relationship("TestCase", back_populates="test_plan_test_cases")
    creator = relationship("User")
    
    # Unique constraint to prevent duplicate associations
    __table_args__ = (
        UniqueConstraint('test_plan_id', 'test_case_id', name='unique_test_plan_test_case'),
    )


class ActivityLog(Base):
    """Model for tracking user activities in the system"""
    __tablename__ = "activity_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_name = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g., 'create', 'update', 'delete', 'login', etc.
    target_type = Column(String, nullable=False)  # e.g., 'test_case', 'project', 'test_execution', etc.
    target_id = Column(String, nullable=False)  # ID of the target entity
    target_name = Column(String, nullable=True)  # Name/title of the target for display
    details = Column(JSON, nullable=True)  # Additional details about the activity
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
