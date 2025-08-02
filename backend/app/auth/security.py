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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
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
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        request: The FastAPI request object
        token: The JWT token from the Authorization header
        db: Async database session
        
    Returns:
        Dict: The authenticated user's information
        
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
        logger.info(f"\n{'='*80}")
        logger.info(f"Authenticating request to {request.url}")
        logger.info(f"Token: {token[:20]}...")
        
        # Decode the JWT token
        try:
            logger.info("Decoding JWT token...")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            logger.info(f"Decoded payload: {payload}")
            
            user_id: str = payload.get("sub")
            if not user_id:
                logger.warning("No user_id (sub) in token payload")
                raise credentials_exception
                
            logger.info(f"Looking up user with ID: {user_id}")
            
            # Get user from database using async query
            result = await db.execute(
                select(models.User).where(models.User.id == user_id)
            )
            user = result.scalars().first()
            
            if not user:
                logger.warning(f"User not found for ID: {user_id}")
                raise credentials_exception
                
            # Log successful authentication
            logger.info(f"Successfully authenticated user: {user.email} (ID: {user.id})")
            
            # Return user info in the expected format
            user_info = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            logger.info(f"Returning user info: {user_info}")
            return user_info
            
        except JWTError as je:
            logger.error(f"JWT validation error: {str(je)}")
            logger.error(f"Token: {token}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise credentials_exception
            
    except HTTPException:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP Exception during authentication: {traceback.format_exc()}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during authentication: {str(e)}"
        )

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_email(self, email: str) -> bool:
        """
        Validate email format and check for existing user
        
        Args:
            email: The email address to validate
            
        Returns:
            bool: True if email is valid and not in use
            
        Raises:
            HTTPException: If email is invalid or already registered
        """
        logger.debug(f"[AUTH_SERVICE] Validating email format for: {email}")
        if not re.match(EMAIL_REGEX, email):
            logger.warning(f"[AUTH_SERVICE] Invalid email format: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
            
        # Check if user already exists
        logger.debug(f"[AUTH_SERVICE] Checking if email exists: {email}")
        try:
            result = await self.db.execute(
                select(models.User).where(models.User.email == email)
            )
            existing_user = result.scalars().first()
            if existing_user:
                logger.warning(f"[AUTH_SERVICE] Email already registered: {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            logger.debug(f"[AUTH_SERVICE] Email validation passed: {email}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"[AUTH_SERVICE] Database error during email validation: {str(e)}")
            logger.error(f"[AUTH_SERVICE] Error type: {type(e).__name__}")
            logger.error(f"[AUTH_SERVICE] Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error validating email"
            )
    
    async def validate_password(self, password: str) -> bool:
        """
        Validate password strength
        
        Args:
            password: The password to validate
            
        Returns:
            bool: True if password meets strength requirements
            
        Raises:
            HTTPException: If password doesn't meet requirements
        """
        logger.debug("[AUTH_SERVICE] Validating password strength")
        
        if not isinstance(password, str) or not password:
            logger.warning("[AUTH_SERVICE] Empty or invalid password provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be empty"
            )
            
        if len(password) < 8:
            logger.warning("[AUTH_SERVICE] Password too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
            
        # Add more password strength checks as needed
        # For example, check for uppercase, lowercase, numbers, special chars
        
        logger.debug("[AUTH_SERVICE] Password validation passed")
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
        logger.info(f"[AUTH_SERVICE] Starting user creation for email: {user_data.get('email')}")
        logger.debug(f"[AUTH_SERVICE] User data: {user_data}")
        
        try:
            # Validate email and password
            logger.debug("[AUTH_SERVICE] Validating email")
            await self.validate_email(user_data['email'])
            logger.debug("[AUTH_SERVICE] Email validation passed")
            
            logger.debug("[AUTH_SERVICE] Validating password")
            await self.validate_password(user_data['password'])
            logger.debug("[AUTH_SERVICE] Password validation passed")
            
            # Hash password
            logger.debug("[AUTH_SERVICE] Hashing password")
            hashed_password = get_password_hash(user_data['password'])
            logger.debug("[AUTH_SERVICE] Password hashed successfully")
            
            # Create user object
            logger.debug("[AUTH_SERVICE] Creating user object")
            user = models.User(
                email=user_data['email'],
                full_name=user_data['full_name'],
                hashed_password=hashed_password,
                role=user_data.get('role', 'tester')
            )
            
            # Add user to database
            logger.debug("[AUTH_SERVICE] Adding user to database")
            self.db.add(user)
            logger.debug("[AUTH_SERVICE] Committing transaction")
            await self.db.commit()
            logger.debug("[AUTH_SERVICE] Refreshing user object")
            await self.db.refresh(user)
            logger.info(f"[AUTH_SERVICE] User created successfully with ID: {user.id}")
            
            # Convert to dict and remove sensitive data
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            logger.debug(f"[AUTH_SERVICE] Returning user data: {user_dict}")
            return user_dict
            
        except HTTPException as he:
            logger.warning(f"[AUTH_SERVICE] Validation error: {str(he.detail)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"[AUTH_SERVICE] Error creating user: {str(e)}")
            logger.error(f"[AUTH_SERVICE] Error type: {type(e).__name__}")
            logger.error(f"[AUTH_SERVICE] Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """
        Get user by ID
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            Optional[dict]: User data if found, None otherwise
        """
        logger.debug(f"[AUTH_SERVICE] Getting user with ID: {user_id}")
        
        if not user_id:
            logger.warning("[AUTH_SERVICE] Empty user ID provided")
            return None
            
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            
            if user:
                user_dict = {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                logger.debug(f"[AUTH_SERVICE] Found user: {user_dict['email']}")
                return user_dict
                
            logger.warning(f"[AUTH_SERVICE] User not found with ID: {user_id}")
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"[AUTH_SERVICE] Database error getting user {user_id}: {str(e)}")
            logger.error(f"[AUTH_SERVICE] Error type: {type(e).__name__}")
            return None
            
        except Exception as e:
            logger.error(f"[AUTH_SERVICE] Unexpected error getting user {user_id}: {str(e)}")
            logger.error(f"[AUTH_SERVICE] Error type: {type(e).__name__}")
            logger.error(f"[AUTH_SERVICE] Traceback: {traceback.format_exc()}")
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
        logger.info(f"[AUTH_SERVICE] Starting authentication for email: {email}")
        
        if not email or not isinstance(email, str):
            logger.warning("[AUTH_SERVICE] Empty or invalid email provided for authentication")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
            
        if not password or not isinstance(password, str):
            logger.warning("[AUTH_SERVICE] Empty or invalid password provided for authentication")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )
        
        try:
            # Find user by email using async SQLAlchemy
            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession
            
            logger.debug("[AUTH_SERVICE] Checking database session type")
            if not isinstance(self.db, AsyncSession):
                error_msg = "Database session is not async"
                logger.error(f"[AUTH_SERVICE] {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg,
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            # Use async query to find user by email
            logger.debug(f"[AUTH_SERVICE] Querying database for user with email: {email}")
            result = await self.db.execute(
                select(models.User).where(models.User.email == email)
            )
            user = result.scalars().first()
            
            if not user:
                logger.warning(f"[AUTH_SERVICE] Authentication failed: No user found with email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            logger.debug(f"[AUTH_SERVICE] User found with ID: {user.id}")
            
            # Verify password
            logger.debug("[AUTH_SERVICE] Verifying password")
            if not verify_password(password, user.hashed_password):
                logger.warning(f"[AUTH_SERVICE] Authentication failed: Incorrect password for email: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            logger.debug("[AUTH_SERVICE] Password verified successfully")
                
            # Convert to dict and remove sensitive data
            user_dict = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            logger.info(f"[AUTH_SERVICE] Authentication successful for user ID: {user.id}")
            logger.debug(f"[AUTH_SERVICE] Returning user data: {user_dict}")
            
            return user_dict
            
        except HTTPException as he:
            logger.warning(f"[AUTH_SERVICE] Authentication failed with HTTPException: {str(he.detail)}")
            raise
            
        except SQLAlchemyError as se:
            logger.error(f"[AUTH_SERVICE] Database error during authentication: {str(se)}")
            logger.error(f"[AUTH_SERVICE] Error type: {type(se).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable"
            )
            
        except Exception as e:
            logger.error(f"[AUTH_SERVICE] Unexpected error during authentication: {str(e)}")
            logger.error(f"[AUTH_SERVICE] Error type: {type(e).__name__}")
            logger.error(f"[AUTH_SERVICE] Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed due to an unexpected error"
            )