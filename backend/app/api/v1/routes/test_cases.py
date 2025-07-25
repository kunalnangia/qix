from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.db import get_db
from app.auth.security import get_current_user
from app.schemas.websocket import TestType, Status, Priority, TestCase, TestCaseCreate, TestCaseUpdate

# Use the imported models directly

router = APIRouter(
    prefix="/test-cases",
    tags=["test-cases"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TestCase, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new test case
    """
    # Check if project exists
    db_project = db.query(models.Project).filter(
        models.Project.id == test_case.project_id
    ).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {test_case.project_id} not found"
        )
    
    # Convert Pydantic model to dict and add required fields
    test_case_data = test_case.dict(exclude={"steps"})
    db_test_case = models.TestCase(
        **test_case_data,
        id=str(uuid.uuid4()),
        created_by=current_user["id"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Add test steps if provided
    if test_case.steps:
        for step in test_case.steps:
            db_step = models.TestStep(
                id=str(uuid.uuid4()),
                test_case_id=db_test_case.id,
                **step.dict()
            )
            db.add(db_step)
    
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    return db_test_case

@router.get("/", response_model=List[TestCase])
async def list_test_cases(
    project_id: Optional[str] = None,
    test_type: Optional[TestType] = None,
    status: Optional[Status] = None,
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List test cases with optional filtering
    """
    query = db.query(models.TestCase)
    
    if project_id:
        query = query.filter(models.TestCase.project_id == project_id)
    if test_type:
        query = query.filter(models.TestCase.test_type == test_type)
    if status:
        query = query.filter(models.TestCase.status == status)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{test_case_id}", response_model=TestCase)
async def get_test_case(
    test_case_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a test case by ID
    """
    db_test_case = db.query(models.TestCase).filter(
        models.TestCase.id == test_case_id
    ).first()
    
    if not db_test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    return db_test_case

@router.put("/{test_case_id}", response_model=TestCase)
async def update_test_case(
    test_case_id: str,
    test_case: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a test case
    """
    db_test_case = db.query(models.TestCase).filter(
        models.TestCase.id == test_case_id
    ).first()
    
    if not db_test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    # Update fields
    update_data = test_case.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_test_case, field, value)
    
    db_test_case.updated_at = datetime.utcnow()
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    return db_test_case

@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a test case
    """
    db_test_case = db.query(models.TestCase).filter(
        models.TestCase.id == test_case_id
    ).first()
    
    if not db_test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    db.delete(db_test_case)
    db.commit()
    
    return None
