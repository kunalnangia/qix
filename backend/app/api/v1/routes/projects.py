from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, Project as ProjectSchema
from app.core.security import get_current_user
from app.services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Create new project.
    """
    return await project_service.create_project(project_data=project_in, user_id=current_user["id"])


@router.get("/", response_model=List[ProjectSchema])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Retrieve projects.
    """
    return await project_service.get_projects(user_id=current_user["id"], skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectSchema)
async def read_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Get project by ID.
    """
    return await project_service.get_project(project_id=project_id, user_id=current_user["id"])


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Update a project.
    """
    return await project_service.update_project(
        project_id=project_id, project_data=project_in, user_id=current_user["id"]
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """
    Delete a project.
    """
    await project_service.delete_project(project_id=project_id, user_id=current_user["id"])
    return None
