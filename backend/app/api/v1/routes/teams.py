from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.team import TeamCreate, TeamUpdate, Team as TeamSchema
from app.core.security import get_current_user
from app.services.team_service import TeamService

router = APIRouter()


def get_team_service(db: AsyncSession = Depends(get_db)) -> TeamService:
    return TeamService(db)


@router.post("/", response_model=TeamSchema, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: TeamCreate,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    """
    Create a new team.
    """
    return await team_service.create_team(
        team_data=team_in, user_id=current_user["id"]
    )


@router.get("/", response_model=List[TeamSchema])
async def read_teams(
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    """
    Retrieve teams.
    """
    return await team_service.get_teams(user_id=current_user["id"])


@router.get("/{team_id}", response_model=TeamSchema)
async def read_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    """
    Get team by ID.
    """
    return await team_service.get_team(team_id=team_id, user_id=current_user["id"])


@router.put("/{team_id}", response_model=TeamSchema)
async def update_team(
    team_id: str,
    team_in: TeamUpdate,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    """
    Update a team.
    """
    return await team_service.update_team(
        team_id=team_id, team_data=team_in, user_id=current_user["id"]
    )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    """
    Delete a team.
    """
    await team_service.delete_team(team_id=team_id, user_id=current_user["id"])
    return None
