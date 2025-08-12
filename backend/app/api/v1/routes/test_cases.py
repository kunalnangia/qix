from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.test_case import (
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
    TestType,
    Status,
)
from app.core.security import get_current_user
from app.services.test_case_service import TestCaseService

router = APIRouter()


def get_test_case_service(db: AsyncSession = Depends(get_db)) -> TestCaseService:
    return TestCaseService(db)


@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case_in: TestCaseCreate,
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service),
):
    """
    Create a new test case.
    """
    return await test_case_service.create_test_case(
        test_case_data=test_case_in, user_id=current_user["id"]
    )


@router.get("/", response_model=List[TestCaseResponse])
async def list_test_cases(
    project_id: Optional[str] = None,
    test_type: Optional[TestType] = None,
    status: Optional[Status] = None,
    limit: int = 100,
    skip: int = 0,
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service),
):
    """
    List test cases with optional filtering.
    """
    return await test_case_service.get_test_cases(
        project_id=project_id,
        test_type=test_type,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: str,
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service),
):
    """
    Get a test case by ID.
    """
    return await test_case_service.get_test_case(test_case_id=test_case_id)


@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: str,
    test_case_in: TestCaseUpdate,
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service),
):
    """
    Update a test case.
    """
    return await test_case_service.update_test_case(
        test_case_id=test_case_id, test_case_data=test_case_in
    )


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: str,
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service),
):
    """
    Delete a test case.
    """
    await test_case_service.delete_test_case(test_case_id=test_case_id)
    return None
