import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import from app modules
from app import schemas
from app.models import db_models as models
from app.db.session import get_db
from app.auth.security import get_current_user

router = APIRouter(
    prefix="/environments",
    tags=["environments"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Environment, status_code=status.HTTP_201_CREATED)
async def create_environment(
    environment: schemas.EnvironmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new environment
    """
    # Check if project exists and user has access
    project = db.query(models.Project).filter(
        models.Project.id == environment.project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {environment.project_id} not found"
        )
    
    # Check if environment with same name already exists in project
    existing_env = db.query(models.Environment).filter(
        models.Environment.project_id == environment.project_id,
        models.Environment.name == environment.name
    ).first()
    
    if existing_env:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Environment with name '{environment.name}' already exists in this project"
        )
    
    # Create environment
    db_environment = models.Environment(
        id=str(uuid.uuid4()),
        name=environment.name,
        description=environment.description,
        base_url=environment.base_url,
        project_id=environment.project_id,
        is_active=environment.is_active if environment.is_active is not None else True,
        variables=environment.variables or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_environment)
    db.commit()
    db.refresh(db_environment)
    
    return db_environment

@router.get("/project/{project_id}", response_model=List[schemas.Environment])
async def list_environments(
    project_id: str,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all environments for a project
    """
    # Check if project exists and user has access
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get environments
    query = db.query(models.Environment).filter(
        models.Environment.project_id == project_id
    )
    
    if active_only:
        query = query.filter(models.Environment.is_active == True)
    
    environments = query.all()
    return environments

@router.get("/{environment_id}", response_model=schemas.Environment)
async def get_environment(
    environment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get environment by ID
    """
    environment = db.query(models.Environment).filter(
        models.Environment.id == environment_id
    ).first()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    return environment

@router.put("/{environment_id}", response_model=schemas.Environment)
async def update_environment(
    environment_id: str,
    environment: schemas.EnvironmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an environment
    """
    db_environment = db.query(models.Environment).filter(
        models.Environment.id == environment_id
    ).first()
    
    if not db_environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    # Update fields if provided
    if environment.name is not None:
        # Check if environment with same name already exists in project
        existing_env = db.query(models.Environment).filter(
            models.Environment.project_id == db_environment.project_id,
            models.Environment.name == environment.name,
            models.Environment.id != environment_id
        ).first()
        
        if existing_env:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Environment with name '{environment.name}' already exists in this project"
            )
        
        db_environment.name = environment.name
    
    if environment.description is not None:
        db_environment.description = environment.description
    
    if environment.base_url is not None:
        db_environment.base_url = environment.base_url
    
    if environment.is_active is not None:
        db_environment.is_active = environment.is_active
    
    if environment.variables is not None:
        db_environment.variables = environment.variables
    
    db_environment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_environment)
    
    return db_environment

@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(
    environment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an environment
    """
    environment = db.query(models.Environment).filter(
        models.Environment.id == environment_id
    ).first()
    
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found"
        )
    
    # Check if environment is being used in any test executions
    execution_count = db.query(models.TestExecution).filter(
        models.TestExecution.environment_id == environment_id
    ).count()
    
    if execution_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete environment that is being used in test executions"
        )
    
    db.delete(environment)
    db.commit()
    
    return None
