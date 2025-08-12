import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.db_models import Project, Team, TeamMember
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_project(self, project_data: ProjectCreate, user_id: str) -> Project:
        if project_data.team_id:
            team = await self.db.get(Team, project_data.team_id)
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {project_data.team_id} not found",
                )

        db_project = Project(
            **project_data.dict(),
            created_by=user_id,
        )
        self.db.add(db_project)
        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project

    async def get_projects(self, user_id: str, skip: int = 0, limit: int = 100) -> list[Project]:
        result = await self.db.execute(
            select(Project)
            .where(
                (Project.created_by == user_id) |
                (Project.team_id.in_(
                    select(TeamMember.team_id).where(TeamMember.user_id == user_id)
                ))
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_project(self, project_id: str, user_id: str) -> Project:
        project = await self.db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # Check if user has access
        is_creator = project.created_by == user_id
        is_member = False
        if project.team_id:
            member = await self.db.execute(
                select(TeamMember).where(
                    TeamMember.team_id == project.team_id,
                    TeamMember.user_id == user_id,
                )
            )
            is_member = member.scalars().first() is not None

        if not is_creator and not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

        return project

    async def update_project(
        self, project_id: str, project_data: ProjectUpdate, user_id: str
    ) -> Project:
        project = await self.db.get(Project, project_id)
        if not project or project.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or you don't have permission to update it",
            )

        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: str, user_id: str):
        project = await self.db.get(Project, project_id)
        if not project or project.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or you don't have permission to delete it",
            )

        await self.db.delete(project)
        await self.db.commit()
        return None
