import logging
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from app.models.db_models import TestCase, TestStep, Project
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, TestType, Status

logger = logging.getLogger(__name__)


class TestCaseService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_test_case(self, test_case_data: TestCaseCreate, user_id: str) -> TestCase:
        project = await self.db.get(Project, test_case_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {test_case_data.project_id} not found",
            )

        db_test_case = TestCase(
            **test_case_data.dict(exclude={"test_steps"}),
            id=str(uuid.uuid4()),
            created_by=user_id,
        )

        if test_case_data.test_steps:
            for step_data in test_case_data.test_steps:
                db_step = TestStep(**step_data.dict(), id=str(uuid.uuid4()))
                db_test_case.test_steps.append(db_step)

        self.db.add(db_test_case)
        await self.db.commit()
        await self.db.refresh(db_test_case)
        return db_test_case

    async def get_test_cases(
        self,
        project_id: Optional[str] = None,
        test_type: Optional[TestType] = None,
        status: Optional[Status] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TestCase]:
        stmt = select(TestCase).options(joinedload(TestCase.test_steps))
        if project_id:
            stmt = stmt.where(TestCase.project_id == project_id)
        if test_type:
            stmt = stmt.where(TestCase.test_type == test_type)
        if status:
            stmt = stmt.where(TestCase.status == status)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_test_case(self, test_case_id: str) -> TestCase:
        stmt = (
            select(TestCase)
            .options(joinedload(TestCase.test_steps))
            .where(TestCase.id == test_case_id)
        )
        result = await self.db.execute(stmt)
        test_case = result.unique().scalars().first()
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test case with id {test_case_id} not found",
            )
        return test_case

    async def update_test_case(
        self, test_case_id: str, test_case_data: TestCaseUpdate
    ) -> TestCase:
        db_test_case = await self.get_test_case(test_case_id)
        update_data = test_case_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_test_case, field, value)

        db_test_case.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(db_test_case)
        return db_test_case

    async def delete_test_case(self, test_case_id: str):
        db_test_case = await self.get_test_case(test_case_id)
        await self.db.delete(db_test_case)
        await self.db.commit()
        return None
