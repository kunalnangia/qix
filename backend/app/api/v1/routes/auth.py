import logging
import sys
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Any, Dict, AsyncGenerator
import traceback
import json

from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserInDB
from app.core.security import get_password_hash, create_access_token, verify_password
from app.core.config import settings
from app.models.db_models import User

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('auth.log')
    ]
)
logger = logging.getLogger(__name__)

# Log environment variables (excluding sensitive data)
env_vars = {k: v for k, v in dict(os.environ).items() if 'PASS' not in k and 'SECRET' not in k}
logger.debug(f"Environment variables: {json.dumps(env_vars, indent=2)}")

# Log database URL (masking password)
if 'DATABASE_URL' in os.environ:
    db_url = os.environ['DATABASE_URL']
    if '@' in db_url:
        protocol, rest = db_url.split('//', 1)
        credentials, host = rest.split('@', 1)
        if ':' in credentials:
            user, _ = credentials.split(':', 1)
            masked_url = f"{protocol}//{user}:*****@{host}"
            logger.debug(f"Database URL: {masked_url}")
    else:
        logger.debug(f"Database URL: {db_url}")

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Log request details
    logger.info(f"\n{'='*80}")
    logger.info(f"Login request received at {datetime.utcnow().isoformat()}")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Client: {request.client}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    # Log form data (excluding password in logs)
    log_form_data = form_data.dict()
    if 'password' in log_form_data:
        log_form_data['password'] = '***'
    logger.info(f"Login attempt for user: {form_data.username}")
    logger.debug(f"Form data: {log_form_data}")
    
    # Log the actual form data received
    try:
        body = await request.body()
        logger.debug(f"Raw request body: {body.decode()}")
    except Exception as e:
        logger.error(f"Error reading request body: {str(e)}")
    
    # Validate form data
    if not form_data.username or not form_data.password:
        logger.error("Missing username or password in form data")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required",
        )
    
    # Log the type of form data
    logger.debug(f"Form data type: {type(form_data).__name__}")
    logger.debug(f"Form data fields: {form_data.__dict__.keys() if hasattr(form_data, '__dict__') else 'No __dict__'}")
    logger.debug(f"Form data values: {form_data.dict() if hasattr(form_data, 'dict') else 'No dict method'}")
    
    # Get database session
    db = None
    try:
        logger.info("Creating database session...")
        db = await anext(get_db())
        logger.info("Database session created successfully")
        
        # Log database info
        logger.debug(f"Database session info: {db}")
        
        # Log SQL query being executed
        query = select(User).where(User.email == form_data.username)
        logger.debug(f"Executing SQL query: {query}")
        
        # Execute query with timing
        start_time = datetime.utcnow()
        result = await db.execute(query)
        query_duration = (datetime.utcnow() - start_time).total_seconds()
        logger.debug(f"Query executed in {query_duration:.4f} seconds")
        
        user = result.scalars().first()
        logger.debug(f"Query result: {'User found' if user else 'No user found'}")
        
        if not user:
            logger.warning(f"Login failed: User {form_data.username} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Log user found (excluding sensitive data)
        user_dict = {k: v for k, v in user.__dict__.items() if not k.startswith('_')}
        if 'hashed_password' in user_dict:
            user_dict['hashed_password'] = '***'
        logger.debug(f"User found: {json.dumps(user_dict, default=str)}")
        
        # Verify password
        logger.info("Verifying password...")
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: Incorrect password for user {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Password verified for user: {user.email}")
        
        # Create access token
        logger.info("Creating access token...")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.id, expires_delta=access_token_expires)
        
        token_data = {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
        logger.info(f"Login successful for user: {user.email}")
        logger.debug(f"Token data: {{'access_token': '***', 'token_type': 'bearer'}}")
        
        return token_data
        
    except HTTPException as he:
        logger.error(f"HTTPException in login: {str(he)}")
        logger.error(f"Status code: {he.status_code}")
        logger.error(f"Detail: {he.detail}")
        logger.error(f"Headers: {he.headers}")
        raise
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        tb = traceback.format_exc()
        
        logger.error(f"Unexpected error in login: {error_type}")
        logger.error(f"Error message: {error_msg}")
        logger.error(f"Traceback:\n{tb}")
        
        # Log database connection status
        if db:
            try:
                logger.debug("Checking database connection status...")
                await db.execute(text("SELECT 1"))
                logger.debug("Database connection is active")
            except Exception as db_error:
                logger.error(f"Database connection error: {str(db_error)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during login: {error_type}: {error_msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    finally:
        if db:
            logger.info("Closing database session...")
            try:
                await db.close()
                logger.info("Database session closed successfully")
            except Exception as e:
                logger.error(f"Error closing database session: {str(e)}")

@router.post("/register", response_model=UserInDB)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new user
    """
    try:
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
        
    except HTTPException as he:
        await db.rollback()
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in user registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )
