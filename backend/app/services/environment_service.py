import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.db_models import Environment, Project
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate

logger = logging.getLogger(__name__)


class EnvironmentService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_environment(
        self, environment_data: EnvironmentCreate, user_id: str
    ) -> Environment:
        project = await self.db.get(Project, environment_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {environment_data.project_id} not found",
            )

        db_environment = Environment(
            **environment_data.dict(),
            id=str(uuid.uuid4()),
            created_by=user_id,
        )
        self.db.add(db_environment)
        await self.db.commit()
        await self.db.refresh(db_environment)
        return db_environment

    async def get_environments_for_project(
        self, project_id: str
    ) -> List[Environment]:
        stmt = select(Environment).where(Environment.project_id == project_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_environment(self, environment_id: str) -> Environment:
        environment = await self.db.get(Environment, environment_id)
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        return environment

    async def update_environment(
        self, environment_id: str, environment_data: EnvironmentUpdate, user_id: str
    ) -> Environment:
        db_environment = await self.get_environment(environment_id)
        if db_environment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this environment",
            )

        update_data = environment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_environment, field, value)

        await self.db.commit()
        await self.db.refresh(db_environment)
        return db_environment

    async def delete_environment(self, environment_id: str, user_id: str):
        db_environment = await self.get_environment(environment_id)
        if db_environment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this environment",
            )

        await self.db.delete(db_environment)
        await self.db.commit()
        return None
