import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
import uuid

from app.db import get_db
from app import models
from app.auth.security import get_current_user
from app.schemas.test_case import (
    TestType, Status, Priority, TestStep, TestStepCreate,
    TestCaseCreate, TestCaseUpdate, TestCaseResponse
)

router = APIRouter(
    prefix="",  # Prefix is handled in main.py
    tags=["test-cases"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new test case
    """
    # Check if project exists
    result = await db.execute(
        select(models.Project).where(models.Project.id == test_case.project_id)
    )
    db_project = result.scalars().first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {test_case.project_id} not found"
        )
    
    # Convert Pydantic model to dict and add required fields
    test_case_data = test_case.dict(exclude={"test_steps"}, exclude_unset=True)
    db_test_case = models.TestCase(
        **test_case_data,
        id=str(uuid.uuid4()),
        created_by=current_user["id"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Add test steps if provided
    if hasattr(test_case, 'test_steps') and test_case.test_steps:
        for step in test_case.test_steps:
            db_step = models.TestStep(
                id=str(uuid.uuid4()),
                test_case_id=db_test_case.id,
                **step.dict()
            )
            db.add(db_step)
    
    db.add(db_test_case)
    await db.commit()
    await db.refresh(db_test_case)
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    return db_test_case

@router.get("/", response_model=List[TestCaseResponse])
async def list_test_cases(
    project_id: Optional[str] = None,
    test_type: Optional[TestType] = None,
    status: Optional[Status] = None,
    limit: int = 100,
    skip: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List test cases with optional filtering
    """
    try:
        # Log the incoming request
        print(f"Fetching test cases with filters - project_id: {project_id}, test_type: {test_type}, status: {status}")
        
        # Start building the query
        stmt = select(models.TestCase).options(joinedload(models.TestCase.test_steps))
        
        # Apply filters
        if project_id:
            stmt = stmt.where(models.TestCase.project_id == project_id)
        if test_type:
            stmt = stmt.where(models.TestCase.test_type == test_type)
        if status:
            stmt = stmt.where(models.TestCase.status == status)
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        # Execute the query
        result = await db.execute(stmt)
        test_cases = result.unique().scalars().all()
        
        # Log the number of test cases found
        print(f"Found {len(test_cases)} test cases")
        
        # Convert to list to force evaluation and catch any serialization errors
        test_cases_list = list(test_cases)
        
        # Log the first test case (if any) for debugging
        if test_cases_list:
            print(f"First test case: {test_cases_list[0].__dict__}")
        
        return test_cases_list
        
    except Exception as e:
        # Log the full error with traceback
        print(f"Error in list_test_cases: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Return a more detailed error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to fetch test cases",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )

@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a test case by ID
    """
    stmt = select(models.TestCase).options(
        joinedload(models.TestCase.test_steps)
    ).where(models.TestCase.id == test_case_id)
    
    result = await db.execute(stmt)
    test_case = result.unique().scalars().first()
    
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    return test_case

@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: str,
    test_case: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a test case
    """
    # Get existing test case
    result = await db.execute(
        select(models.TestCase).where(models.TestCase.id == test_case_id)
    )
    db_test_case = result.scalars().first()
    
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
    await db.commit()
    await db.refresh(db_test_case)
    
    return db_test_case

@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a test case
    """
    result = await db.execute(
        select(models.TestCase).where(models.TestCase.id == test_case_id)
    )
    db_test_case = result.scalars().first()
    
    if not db_test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    await db.delete(db_test_case)
    await db.commit()
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    return None
