from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class ExecutionResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NOT_EXECUTED = "not_executed"

class TestExecutionBase(BaseModel):
    test_case_id: str
    environment_id: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    actual_result: Optional[str] = Field(None, max_length=2000)

class TestExecutionCreate(TestExecutionBase):
    """Schema for creating a test execution"""
    pass

class TestExecutionUpdate(BaseModel):
    """Schema for updating a test execution"""
    status: Optional[ExecutionStatus] = None
    result: Optional[ExecutionResult] = None
    notes: Optional[str] = Field(None, max_length=2000)
    actual_result: Optional[str] = Field(None, max_length=2000)
    error_message: Optional[str] = Field(None, max_length=1000)
    screenshots: Optional[List[str]] = None
    logs: Optional[str] = Field(None, max_length=10000)

class TestExecutionInDBBase(TestExecutionBase):
    id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[ExecutionResult] = None
    executed_by: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None  # Duration in seconds
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    screenshots: List[str] = []
    logs: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "test_case_id": "123e4567-e89b-12d3-a456-426614174000",
                "environment_id": "env-123",
                "status": "completed",
                "result": "pass",
                "executed_by": "user-123",
                "started_at": "2023-01-01T12:00:00Z",
                "completed_at": "2023-01-01T12:02:30Z",
                "duration": 150.5,
                "notes": "Test execution completed successfully",
                "actual_result": "All test steps passed",
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T12:02:30Z",
                "error_message": None,
                "screenshots": [],
                "logs": None
            }
        }

class TestExecutionResponse(TestExecutionInDBBase):
    """Response schema for test execution data"""
    pass
    model_config = ConfigDict(from_attributes=True)

class TestExecution(TestExecutionInDBBase):
    """Schema for returning test execution data to client"""
    pass

class TestExecutionInDB(TestExecutionInDBBase):
    """Schema for test execution data stored in database"""
    pass

class TestExecutionSummary(BaseModel):
    """Summary schema for test execution statistics"""
    total_executions: int
    passed: int
    failed: int
    blocked: int
    not_executed: int
    pass_rate: float = Field(..., ge=0.0, le=100.0)
    average_duration: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class BulkTestExecutionCreate(BaseModel):
    """Schema for creating multiple test executions"""
    test_case_ids: List[str] = Field(..., min_items=1, max_items=100)
    environment_id: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    
class BulkTestExecutionResult(BaseModel):
    """Result schema for bulk test execution creation"""
    created_count: int
    execution_ids: List[str]
    failed_count: int = 0
    errors: List[str] = []
