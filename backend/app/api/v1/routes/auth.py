import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from typing import Any
import traceback

from app.db.session import get_async_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserInDB
from app.core.security import get_password_hash, create_access_token, verify_password
from app.core.config import settings
from app.models.db_models import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Use async query to find the user
        logger.debug("Executing database query to find user")
        result = await db.execute(
            select(User).where(User.email == form_data.username)
        )
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"Login failed: User {form_data.username} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        logger.debug("Verifying password")
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: Incorrect password for user {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Login successful for user: {user.email}")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
        logger.debug("Login token generated successfully")
        return token_data
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as they are
        logger.warning(f"HTTPException in login: {str(he)}")
        raise
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in login: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=UserInDB)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db)
) -> Any:
    """
    Create new user
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    
    # Add and commit the new user
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
