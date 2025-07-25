from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

# Import Base from the models package to avoid circular imports
from ..models import Base

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_cases = relationship("TestCase", back_populates="creator", lazy="selectin")
    comments = relationship("Comment", back_populates="user", lazy="selectin")
    test_executions = relationship("TestExecution", back_populates="executor", lazy="selectin")

# Project Model
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    
    # Relationships
    test_cases = relationship("TestCase", backref="project", lazy="selectin")
    test_plans = relationship("TestPlan", backref="project", lazy="selectin")
    team = relationship("Team", backref="projects", lazy="selectin")
    environments = relationship("Environment", backref="project", lazy="selectin")

# Test Step Model (for TestCase)
class TestStep(Base):
    __tablename__ = "test_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    test_case_id = Column(String, ForeignKey("test_cases.id"), nullable=False)
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
    project = relationship("Project", back_populates="test_cases", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], back_populates="test_cases", lazy="selectin")
    assignee = relationship("User", foreign_keys=[assigned_to], lazy="selectin")
    steps = relationship("TestStep", back_populates="test_case", cascade="all, delete-orphan", lazy="selectin")
    test_executions = relationship("TestExecution", back_populates="test_case", lazy="selectin")
    comments = relationship("Comment", back_populates="test_case", lazy="selectin")

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
    project = relationship("Project", back_populates="test_plans", lazy="selectin")
    test_executions = relationship("TestExecution", back_populates="test_plan", lazy="selectin")
    test_cases = relationship("TestCase", secondary="test_plan_test_cases", back_populates="test_plans", lazy="selectin")

# Association table for many-to-many relationship between TestPlan and TestCase
class TestPlanTestCase(Base):
    __tablename__ = "test_plan_test_cases"
    
    test_plan_id = Column(String, ForeignKey("test_plans.id"), primary_key=True)
    test_case_id = Column(String, ForeignKey("test_cases.id"), primary_key=True)

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
    test_case = relationship("TestCase", back_populates="test_executions", lazy="selectin")
    test_plan = relationship("TestPlan", back_populates="test_executions", lazy="selectin")
    executor = relationship("User", back_populates="test_executions", lazy="selectin")
    environment = relationship("Environment", back_populates="test_executions", lazy="selectin")

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
    test_case = relationship("TestCase", back_populates="comments", lazy="selectin")
    user = relationship("User", back_populates="comments", lazy="selectin")
    parent_comment = relationship("Comment", remote_side=[id], backref="replies", lazy="selectin")


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
    members = relationship("TeamMember", back_populates="team", lazy="selectin")
    projects = relationship("Project", back_populates="team", lazy="selectin")


# Team Member Model (for many-to-many relationship between User and Team)
class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # member, admin, owner
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="members", lazy="selectin")
    user = relationship("User", lazy="selectin")


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
    project = relationship("Project", back_populates="environments", lazy="selectin")
    test_executions = relationship("TestExecution", back_populates="environment", lazy="selectin")


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
    uploader = relationship("User", lazy="selectin")
