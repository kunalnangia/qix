import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.db_models import Team, TeamMember, User
from app.schemas.team import TeamCreate, TeamUpdate

logger = logging.getLogger(__name__)


class TeamService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_team(self, team_data: TeamCreate, user_id: str) -> Team:
        db_team = Team(
            **team_data.dict(),
            id=str(uuid.uuid4()),
            created_by=user_id,
        )
        self.db.add(db_team)
        await self.db.commit()
        await self.db.refresh(db_team)
        return db_team

    async def get_teams(self, user_id: str) -> List[Team]:
        stmt = select(Team).where(
            (Team.created_by == user_id)
            | (Team.members.any(TeamMember.user_id == user_id))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_team(self, team_id: str, user_id: str) -> Team:
        team = await self.db.get(Team, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )
        # Add access control logic if needed
        return team

    async def update_team(
        self, team_id: str, team_data: TeamUpdate, user_id: str
    ) -> Team:
        db_team = await self.get_team(team_id, user_id)
        if db_team.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this team",
            )

        update_data = team_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_team, field, value)

        await self.db.commit()
        await self.db.refresh(db_team)
        return db_team

    async def delete_team(self, team_id: str, user_id: str):
        db_team = await self.get_team(team_id, user_id)
        if db_team.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this team",
            )

        await self.db.delete(db_team)
        await self.db.commit()
        return None
