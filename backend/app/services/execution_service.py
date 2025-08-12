import logging
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.db_models import TestExecution, TestCase
from app.schemas.execution import TestExecutionCreate, ExecutionStatus

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_test_execution(
        self, execution_data: TestExecutionCreate, user_id: str
    ) -> TestExecution:
        db_execution = TestExecution(
            **execution_data.dict(),
            id=str(uuid.uuid4()),
            executed_by=user_id,
        )
        self.db.add(db_execution)
        await self.db.commit()
        await self.db.refresh(db_execution)
        return db_execution

    async def get_test_executions(
        self, test_case_id: Optional[str] = None
    ) -> List[TestExecution]:
        stmt = select(TestExecution)
        if test_case_id:
            stmt = stmt.where(TestExecution.test_case_id == test_case_id)
        stmt = stmt.order_by(TestExecution.created_at.desc()).limit(100)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_execution_status(
        self, execution_id: str, new_status: ExecutionStatus
    ) -> TestExecution:
        execution = await self.db.get(TestExecution, execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test execution not found",
            )

        execution.status = new_status
        execution.updated_at = datetime.utcnow()

        if new_status == ExecutionStatus.RUNNING:
            execution.started_at = datetime.utcnow()
        elif new_status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            execution.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(execution)
        return execution
