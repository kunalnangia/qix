from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.db_models import TestExecution, ExecutionStatus
from app.models.db_models import TestCase as DBTestCase
from app.models.db_models import User
from app.schemas.execution import TestExecutionCreate, TestExecutionInDB
from app.core.security import get_current_user

router = APIRouter(prefix="/executions", tags=["executions"])

@router.post("/", response_model=TestExecutionInDB, status_code=status.HTTP_201_CREATED)
def create_test_execution(
    execution_in: TestExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new test execution record
    """
    # Verify test case exists and user has access
    test_case = db.query(TestCase).filter(
        (TestCase.id == execution_in.test_case_id) &
        (TestCase.created_by == current_user.id)
    ).first()
    
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found or access denied"
        )
    
    execution = TestExecution(
        id=str(uuid.uuid4()),
        test_case_id=execution_in.test_case_id,
        status=ExecutionStatus.PENDING,
        started_by=current_user.id,
        started_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Update test case status
    test_case.status = ExecutionStatus.IN_PROGRESS
    test_case.updated_at = datetime.utcnow()
    
    db.add(execution)
    db.add(test_case)
    db.commit()
    db.refresh(execution)
    
    return execution

@router.get("/{execution_id}", response_model=TestExecutionInDB)
def get_test_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a test execution by ID
    """
    execution = db.query(TestExecution).join(
        TestCase,
        TestExecution.test_case_id == TestCase.id
    ).filter(
        (TestExecution.id == execution_id) &
        (TestCase.created_by == current_user.id)
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test execution not found or access denied"
        )
    
    return execution

@router.get("/test-case/{test_case_id}", response_model=List[TestExecutionInDB])
def get_test_case_executions(
    test_case_id: str,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all executions for a test case
    """
    # Verify test case exists and user has access
    test_case = db.query(TestCase).filter(
        (TestCase.id == test_case_id) &
        (TestCase.created_by == current_user.id)
    ).first()
    
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found or access denied"
        )
    
    executions = db.query(TestExecution).filter(
        TestExecution.test_case_id == test_case_id
    ).order_by(
        TestExecution.started_at.desc()
    ).offset(skip).limit(limit).all()
    
    return executions

@router.put("/{execution_id}/status/{status}", response_model=TestExecutionInDB)
def update_execution_status(
    execution_id: str,
    status: ExecutionStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of a test execution
    """
    execution = db.query(TestExecution).join(
        TestCase,
        TestExecution.test_case_id == TestCase.id
    ).filter(
        (TestExecution.id == execution_id) &
        (TestCase.created_by == current_user.id)
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test execution not found or access denied"
        )
    
    # Update execution status
    execution.status = status
    execution.updated_at = datetime.utcnow()
    
    # If execution is completed, update the test case status
    if status in [ExecutionStatus.PASSED, ExecutionStatus.FAILED, ExecutionStatus.BLOCKED]:
        execution.completed_at = datetime.utcnow()
        
        # Update test case status
        test_case = db.query(TestCase).filter(
            TestCase.id == execution.test_case_id
        ).first()
        
        if test_case:
            test_case.status = status
            test_case.updated_at = datetime.utcnow()
            db.add(test_case)
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    return execution
