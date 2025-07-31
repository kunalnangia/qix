from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Simplified enums for debugging
class TestType(str, Enum):
    FUNCTIONAL = "functional"
    API = "api"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"

# Minimal TestStep model
class TestStepBase(BaseModel):
    step_number: int
    description: str
    expected_result: str

class TestStepCreate(TestStepBase):
    pass

class TestStep(TestStepBase):
    id: str
    test_case_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Minimal TestCase model
class TestCaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    test_type: TestType = TestType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    status: Status = Status.DRAFT

class TestCaseCreate(TestCaseBase):
    project_id: str
    test_steps: List[TestStepCreate] = []

class TestCaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[TestType] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None

# Simplified response model
class TestCaseResponse(TestCaseBase):
    id: str
    project_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    test_steps: List[TestStep] = []
    
    model_config = ConfigDict(from_attributes=True)
