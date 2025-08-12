from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.execution import (
    TestExecutionCreate,
    TestExecutionResponse,
    ExecutionStatus,
)
from app.core.security import get_current_user
from app.services.execution_service import ExecutionService
from app.websocket.manager import websocket_manager

router = APIRouter()


def get_execution_service(db: AsyncSession = Depends(get_db)) -> ExecutionService:
    return ExecutionService(db)


@router.post("/", response_model=TestExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_test_execution(
    execution_in: TestExecutionCreate,
    current_user: dict = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """
    Create a new test execution.
    """
    execution = await execution_service.create_test_execution(
        execution_data=execution_in, user_id=current_user["id"]
    )
    await websocket_manager.broadcast_test_execution_update(execution.dict())
    return execution


@router.get("/", response_model=List[TestExecutionResponse])
async def get_test_executions(
    test_case_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """
    Get test executions.
    """
    return await execution_service.get_test_executions(test_case_id=test_case_id)


@router.put("/{execution_id}/status", response_model=TestExecutionResponse)
async def update_execution_status(
    execution_id: str,
    status: ExecutionStatus,
    current_user: dict = Depends(get_current_user),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """
    Update execution status.
    """
    execution = await execution_service.update_execution_status(
        execution_id=execution_id, new_status=status
    )
    await websocket_manager.broadcast_test_execution_update(execution.dict())
    return execution
