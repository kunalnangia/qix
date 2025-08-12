import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.db_models import User
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(self, user_data: dict) -> dict:
        """
        Creates a new user in the database.
        """
        existing_user = await self.get_user_by_email(user_data["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )

        hashed_password = get_password_hash(user_data["password"])
        db_user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data.get("full_name"),
            role=user_data.get("role", "tester"),
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role,
        }

    async def authenticate_user(self, email: str, password: str) -> dict | None:
        """
        Authenticates a user by email and password.
        """
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }

    async def get_user(self, user_id: str) -> dict | None:
        """
        Retrieves a user by their ID.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email address.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
