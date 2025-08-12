import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectInDB
from app.core.security import get_current_user
from app.models.db_models import User
from app.core.redis import redis_client

router = APIRouter()

@router.get("/", response_model=List[ProjectInDB])
def read_projects(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve projects. Only returns projects the user has access to.
    """
    projects = db.query(Project).filter(
        Project.created_by == current_user.id
    ).offset(skip).limit(limit).all()
    return projects

@router.post("/", response_model=ProjectInDB, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new project.
    """
    project = Project(
        **project_in.dict(),
        created_by=current_user.id,
        is_active=True
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectInDB)
def read_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project by ID.
    This endpoint uses Redis for caching.
    """
    cache_key = f"project:{project_id}"

    # Try to get the project from cache
    cached_project = redis_client.get(cache_key)
    if cached_project:
        return json.loads(cached_project)

    # If not in cache, get from database
    project = db.query(Project).filter(
        (Project.id == project_id) & 
        (Project.created_by == current_user.id)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )

    # Serialize and store in cache for 1 hour
    project_data = ProjectInDB.from_orm(project).json()
    redis_client.set(cache_key, project_data, ex=3600)

    return project

@router.put("/{project_id}", response_model=ProjectInDB)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a project.
    """
    project = db.query(Project).filter(
        (Project.id == project_id) & 
        (Project.created_by == current_user.id)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )
    
    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)

    # Invalidate cache
    cache_key = f"project:{project_id}"
    redis_client.delete(cache_key)

    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project.
    """
    project = db.query(Project).filter(
        (Project.id == project_id) & 
        (Project.created_by == current_user.id)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )
    
    db.delete(project)
    db.commit()

    # Invalidate cache
    cache_key = f"project:{project_id}"
    redis_client.delete(cache_key)

    return None
