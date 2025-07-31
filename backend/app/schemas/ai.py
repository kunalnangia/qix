from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class AIModelType(str, Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude"

class TestGenerationType(str, Enum):
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UNIT = "unit"
    PERFORMANCE = "performance"
    API = "api"
    UI = "ui"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AIAnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AITestGenerationRequest(BaseModel):
    """Request schema for AI test case generation"""
    prompt: str = Field(..., min_length=10, max_length=2000, description="Description of what to test")
    project_id: str = Field(..., description="Project ID to associate test cases with")
    test_type: TestGenerationType = TestGenerationType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    count: int = Field(default=5, ge=1, le=20, description="Number of test cases to generate")
    model: AIModelType = AIModelType.GPT4
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Generate test cases for user login functionality",
                "project_id": "proj_123",
                "test_type": "functional",
                "priority": "high",
                "count": 5
            }
        }
    )

class AIDebugRequest(BaseModel):
    """Request schema for AI test debugging"""
    execution_id: str = Field(..., description="Test execution ID")
    test_case_id: str = Field(..., description="Test case ID")
    error_description: str = Field(..., min_length=10, max_length=2000)
    logs: Optional[str] = Field(None, max_length=10000, description="Error logs or stack trace")
    environment_info: Optional[Dict[str, Any]] = Field(None, description="Environment details")
    model: AIModelType = AIModelType.GPT4

class AIPrioritizationRequest(BaseModel):
    """Request schema for AI test case prioritization"""
    test_case_ids: List[str] = Field(..., min_items=2, max_items=100)
    context: str = Field(..., min_length=10, max_length=1000, description="Context for prioritization")
    criteria: Optional[List[str]] = Field(None, description="Prioritization criteria")
    model: AIModelType = AIModelType.GPT4

class AIAnalysisResult(BaseModel):
    """Result schema for AI analysis"""
    analysis: str = Field(..., description="AI analysis result")
    suggestions: List[str] = Field(default=[], description="AI suggestions")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the analysis")
    root_cause: Optional[str] = Field(None, description="Identified root cause")
    fix_suggestions: List[str] = Field(default=[], description="Suggested fixes")
    related_issues: List[str] = Field(default=[], description="Related issues found")
    
    model_config = ConfigDict(from_attributes=True)

class AITestCaseGeneration(BaseModel):
    """Result schema for AI generated test cases"""
    generated_count: int
    test_cases: List[Dict[str, Any]]
    generation_time: float
    model_used: AIModelType
    
    model_config = ConfigDict(from_attributes=True)

class AIPrioritizationResult(BaseModel):
    """Result schema for AI test case prioritization"""
    prioritized_test_case_ids: List[str]
    prioritization_reasoning: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    
    model_config = ConfigDict(from_attributes=True)
