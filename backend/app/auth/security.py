from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
import traceback
import re

from app.db import get_db
from app.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Import SQLAlchemy models
from app.models import db_models as models
from app.db.session import get_db

security = HTTPBearer()

# Email validation regex
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,}$'

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    try:
        if not plain_password or not hashed_password:
            logger.warning("Empty password or hash provided for verification")
            return False
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password for storing.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
        
    Raises:
        ValueError: If password is empty or None
    """
    try:
        if not password:
            raise ValueError("Password cannot be empty")
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        logger.debug(traceback.format_exc())
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: The encoded JWT token
        
    Raises:
        JWTError: If there's an error encoding the token
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as je:
        logger.error(f"JWT Error creating access token: {str(je)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating access token: {str(e)}")
        logger.debug(traceback.format_exc())
        raise

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception

    """
    Get the current authenticated user from the JWT token.
    
    Args:
        request: The FastAPI request object
        token: The JWT token from the Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Log the request for debugging
        logger.info(f"Authenticating request to {request.url}")
        
        # Decode the JWT token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if not username:
                logger.warning("No username in token")
                raise credentials_exception
        except JWTError as je:
            logger.warning(f"JWT validation failed: {str(je)}")
            db: Session = get_db()
            user = db.query(models.User).filter(models.User.id == user_id).first()
            
            if not user:
                logger.warning(f"User not found for ID: {user_id}")
                raise credentials_exception
                
            # Log successful authentication
            logger.info(f"Successfully authenticated user: {user.email}")
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise credentials_exception
            
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        )

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def validate_email(self, email: str) -> bool:
        """Validate email format and check for existing user"""
        if not re.match(EMAIL_REGEX, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
            
        # Check if user already exists
        existing_user = self.db.query(models.User).filter(models.User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        return True
    
    async def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        return True
    
    async def create_user(self, user_data: dict) -> dict:
        """
        Create a new user with validation
        
        Args:
            user_data: Dictionary containing user registration data
            
        Returns:
            Dict containing the created user data
            
        Raises:
            HTTPException: If validation fails or user creation fails
        """
        try:
            # Validate email and password
            await self.validate_email(user_data['email'])
            self.validate_password(user_data['password'])
            
            # Hash password
            hashed_password = get_password_hash(user_data['password'])
            
            # Create user object
            user = models.User(
                email=user_data['email'],
                full_name=user_data['full_name'],
                hashed_password=hashed_password,
                role=user_data.get('role', 'tester')
            )
            
            # Add user to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Convert to dict and remove sensitive data
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            return user_dict
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticate user with email and password
        
        Args:
            email: User's email address
            password: User's plain text password
            
        Returns:
            User dictionary if authentication is successful
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Find user by email using async SQLAlchemy
            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession
            
            if not isinstance(self.db, AsyncSession):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session is not async",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # Use async query
            result = await self.db.execute(
                select(models.User).where(models.User.email == email)
            )
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # Verify password
            if not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # Convert to dict and remove sensitive data
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            return user_dict
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )