from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.db_models import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectInDB
from app.core.security import get_current_user
from app.models.db_models import User

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
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project by ID.
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
    return project

@router.put("/{project_id}", response_model=ProjectInDB)
def update_project(
    project_id: int,
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
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
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
    return None
