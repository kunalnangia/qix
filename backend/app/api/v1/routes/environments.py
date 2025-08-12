from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.environment import (
    EnvironmentCreate,
    EnvironmentUpdate,
    Environment as EnvironmentSchema,
)
from app.core.security import get_current_user
from app.services.environment_service import EnvironmentService

router = APIRouter()


def get_environment_service(db: AsyncSession = Depends(get_db)) -> EnvironmentService:
    return EnvironmentService(db)


@router.post("/", response_model=EnvironmentSchema, status_code=status.HTTP_201_CREATED)
async def create_environment(
    environment_in: EnvironmentCreate,
    current_user: dict = Depends(get_current_user),
    environment_service: EnvironmentService = Depends(get_environment_service),
):
    """
    Create a new environment.
    """
    return await environment_service.create_environment(
        environment_data=environment_in, user_id=current_user["id"]
    )


@router.get("/project/{project_id}", response_model=List[EnvironmentSchema])
async def get_environments_for_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    environment_service: EnvironmentService = Depends(get_environment_service),
):
    """
    Get all environments for a project.
    """
    return await environment_service.get_environments_for_project(project_id=project_id)


@router.get("/{environment_id}", response_model=EnvironmentSchema)
async def get_environment(
    environment_id: str,
    current_user: dict = Depends(get_current_user),
    environment_service: EnvironmentService = Depends(get_environment_service),
):
    """
    Get an environment by ID.
    """
    return await environment_service.get_environment(environment_id=environment_id)


@router.put("/{environment_id}", response_model=EnvironmentSchema)
async def update_environment(
    environment_id: str,
    environment_in: EnvironmentUpdate,
    current_user: dict = Depends(get_current_user),
    environment_service: EnvironmentService = Depends(get_environment_service),
):
    """
    Update an environment.
    """
    return await environment_service.update_environment(
        environment_id=environment_id,
        environment_data=environment_in,
        user_id=current_user["id"],
    )


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(
    environment_id: str,
    current_user: dict = Depends(get_current_user),
    environment_service: EnvironmentService = Depends(get_environment_service),
):
    """
    Delete an environment.
    """
    await environment_service.delete_environment(
        environment_id=environment_id, user_id=current_user["id"]
    )
    return None
