from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class ActivityType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    EXECUTED = "executed"
    COMMENTED = "commented"
    GENERATED = "generated"

class TargetType(str, Enum):
    PROJECT = "project"
    TEST_CASE = "test_case"
    TEST_EXECUTION = "test_execution"
    COMMENT = "comment"
    USER = "user"

class ActivityFeed(BaseModel):
    """Schema for activity feed entries"""
    id: Optional[str] = None
    user_id: str
    user_name: str
    action: ActivityType
    target_type: TargetType
    target_id: str
    target_name: str
    description: str = Field(..., max_length=500)
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": "user_123",
                "user_name": "John Doe",
                "action": "created",
                "target_type": "test_case",
                "target_id": "tc_456",
                "target_name": "Login Test",
                "description": "Created test case: Login Test",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    )

class TestCaseStats(BaseModel):
    """Test case statistics"""
    total: int = 0
    by_status: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    by_type: Dict[str, int] = {}

class ExecutionStats(BaseModel):
    """Test execution statistics"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    blocked: int = 0
    not_executed: int = 0
    pass_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    trend: List[Dict[str, Any]] = []  # Historical trend data

class ProjectStats(BaseModel):
    """Project statistics"""
    total_projects: int = 0
    active_projects: int = 0
    test_cases_per_project: Dict[str, int] = {}

class DashboardStats(BaseModel):
    """Main dashboard statistics schema"""
    total_test_cases: int = 0
    total_executions: int = 0
    pass_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    average_execution_time: float = 0.0  # in seconds
    active_test_runs: int = 0
    recent_activity: List[ActivityFeed] = []
    
    # Detailed statistics
    test_case_stats: Optional[TestCaseStats] = None
    execution_stats: Optional[ExecutionStats] = None
    project_stats: Optional[ProjectStats] = None
    
    # Time-based data
    executions_today: int = 0
    executions_this_week: int = 0
    executions_this_month: int = 0
    
    # Trend data
    daily_execution_trend: List[Dict[str, Any]] = []
    pass_rate_trend: List[Dict[str, Any]] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "total_test_cases": 150,
                "total_executions": 1200,
                "pass_rate": 85.5,
                "average_execution_time": 45.2,
                "active_test_runs": 3,
                "executions_today": 25,
                "executions_this_week": 180,
                "executions_this_month": 750
            }
        }
    )

class DashboardFilter(BaseModel):
    """Dashboard filter options"""
    project_ids: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    test_types: Optional[List[str]] = None
    priorities: Optional[List[str]] = None
    
class ChartData(BaseModel):
    """Generic chart data schema"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    
class ReportData(BaseModel):
    """Test report data schema"""
    title: str
    generated_at: datetime
    period: str
    summary: DashboardStats
    charts: Dict[str, ChartData]
    
    model_config = ConfigDict(from_attributes=True)
