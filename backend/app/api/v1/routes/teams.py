from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.db import get_db
from app.auth.security import get_current_user
from app.schemas.websocket import Team, TeamCreate, TeamMember, TeamMemberCreate, TeamDetail

# Create a simple namespace for schemas to maintain compatibility
class SchemaNamespace:
    pass

schemas = SchemaNamespace()
schemas.Team = Team
schemas.TeamCreate = TeamCreate
schemas.TeamMember = TeamMember
schemas.TeamMemberCreate = TeamMemberCreate
schemas.TeamDetail = TeamDetail

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Team, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: schemas.TeamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new team
    """
    # Check if team name already exists
    db_team = db.query(models.Team).filter(
        models.Team.name == team.name
    ).first()
    
    if db_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name already exists"
        )
    
    # Create team
    db_team = models.Team(
        id=str(uuid.uuid4()),
        name=team.name,
        description=team.description,
        created_by=current_user["id"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    # Add creator as team owner
    db_member = models.TeamMember(
        id=str(uuid.uuid4()),
        team_id=db_team.id,
        user_id=current_user["id"],
        role="owner",
        joined_at=datetime.utcnow()
    )
    
    db.add(db_member)
    db.commit()
    
    return db_team

@router.get("/", response_model=List[schemas.Team])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all teams
    """
    # Get teams where user is a member
    teams = db.query(models.Team).join(
        models.TeamMember,
        models.Team.id == models.TeamMember.team_id
    ).filter(
        models.TeamMember.user_id == current_user["id"]
    ).offset(skip).limit(limit).all()
    
    return teams

@router.get("/{team_id}", response_model=schemas.TeamDetail)
async def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get team details by ID
    """
    # Check if user is a member of the team
    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id,
        models.TeamMember.user_id == current_user["id"]
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team"
        )
    
    # Get team with members
    team = db.query(models.Team).filter(
        models.Team.id == team_id
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get team members
    members = db.query(
        models.User,
        models.TeamMember.role,
        models.TeamMember.joined_at
    ).join(
        models.TeamMember,
        models.User.id == models.TeamMember.user_id
    ).filter(
        models.TeamMember.team_id == team_id
    ).all()
    
    # Format response
    member_list = [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": role,
            "joined_at": joined_at
        }
        for user, role, joined_at in members
    ]
    
    return {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "created_at": team.created_at,
        "updated_at": team.updated_at,
        "members": member_list
    }

@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: str,
    member: schemas.TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a member to a team
    """
    # Check if user has permission to add members (must be team admin or owner)
    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id,
        models.TeamMember.user_id == current_user["id"],
        models.TeamMember.role.in_(["admin", "owner"])
    ).first()
    
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add members to this team"
        )
    
    # Check if team exists
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == member.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already a member of the team
    existing_member = db.query(models.TeamMember).filter(
        models.TeamMember.team_id == team_id,
        models.TeamMember.user_id == member.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this team"
        )
    
    # Add user to team
    db_member = models.TeamMember(
        id=str(uuid.uuid4()),
        team_id=team_id,
        user_id=member.user_id,
        role=member.role,
        joined_at=datetime.utcnow()
    )
    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    return {"message": "Member added to team successfully"}
