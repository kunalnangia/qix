import logging
import uuid
import traceback
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token
from app.auth.security import create_access_token, get_current_user
from app.auth.service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    """
    request_id = str(uuid.uuid4())
    logger.info(f"[REGISTER-{request_id}] Starting registration for email: {user_data.email}")
    
    try:
        auth_service = AuthService(db)
        user_data_dict = {
            "email": user_data.email,
            "password": user_data.password,
            "full_name": user_data.full_name,
            "role": "tester"  # Default role
        }
        
        user = await auth_service.create_user(user_data_dict)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {"sub": str(user["id"]), "email": user["email"], "role": user["role"]}
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException as http_exc:
        logger.error(f"[REGISTER] HTTP Exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"[REGISTER] Unexpected error during registration: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an unexpected error"
        )


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate_user(form_data.email, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during login for {form_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user's information
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user(current_user["id"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )
