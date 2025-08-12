import os
import sys
import logging
import json
import traceback
import uuid  # For generating unique request IDs
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Union
from contextlib import asynccontextmanager
from pathlib import Path
from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request, status, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.session import get_db
from app.models.db_models import (
    Project as DBProject, 
    User, 
    Team, 
    TestCase, 
    TestStep, 
    TestPlan, 
    TestExecution,
    Comment as DBComment,
    TestStep,
    TestPlanTestCase,
    TeamMember,
    Environment,
    Attachment,
    ActivityLog
)
    
# Configure logging
if not os.path.exists("logs"):
    os.makedirs("logs")

# Create a custom formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Configure root logger
logger = logging.getLogger()

# Set log level from environment variable or default to INFO
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

# Clear any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create formatters
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Add file handler with rotation
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(
    "logs/app.log", 
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Log startup message
logger.info("=" * 80)
logger.info(f"Application starting with enhanced logging (level: {log_level})")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info("=" * 80)

# Get logger for this module
logger = logging.getLogger(__name__)

# Enable SQLAlchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.orm').setLevel(logging.INFO)


# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import models first to ensure they are registered with SQLAlchemy
from app.models.db_models import (
    Project as DBProject, 
    User, 
    Team, 
    TestCase, 
    TestExecution, 
    Comment as DBComment,
    TestStep,
    TestPlan,
    TestPlanTestCase,
    TeamMember,
    Environment,
    Attachment,
    ActivityLog
)

import asyncio
from sqlalchemy.exc import OperationalError

async def initialize_database():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (Attempt {attempt + 1}/{max_retries})")
            logger.debug(f"Using connection string: {os.getenv('DATABASE_URL')}")
            
            with sync_engine.connect() as conn:
                # Test the connection with a simple query
                result = conn.execute(text("SELECT version();"))
                version = result.scalar()
                logger.info(f"Successfully connected to PostgreSQL version: {version}")
                
                # Check if tables exist
                table_check = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """))
                tables = [row[0] for row in table_check]
                logger.info(f"Found {len(tables)} tables in the database")
                if tables:
                    logger.debug(f"Tables: {', '.join(tables)}")
                
                logger.info("Database connection test successful")
                return True
                
        except Exception as e:
            logger.error(f"Database connection error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)  # Exponential backoff
                logger.warning(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.critical("Max retries reached. Could not connect to database.")
                raise

# Import API routers
from app.api.v1.routes import (
    test_cases,
    teams,
    environments,
    attachments,
    projects,
    comments,
    auth,
    executions,
    ai
)

# Import schemas
from app.schemas.user import UserCreate, UserLogin
from app.schemas.project import ProjectCreate, Project as ProjectResponse, ProjectUpdate  
from app.schemas.test_case import TestCaseResponse, TestCaseCreate, TestCaseUpdate
from app.schemas.comment import CommentCreate, Comment as CommentResponse, CommentInDB
from app.schemas.ai import AITestGenerationRequest, AIDebugRequest, AIPrioritizationRequest, AIAnalysisResult, AIAnalysisStatus
from app.schemas.execution import TestExecutionCreate, TestExecutionResponse, ExecutionStatus
from app.schemas.dashboard import DashboardStats, ActivityFeed

# FastAPI imports
from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder

# SQLAlchemy imports
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Application imports
from app.db.session import SessionLocal, init_db, engine, get_db
from app.auth.security import get_current_user, create_access_token, get_password_hash, verify_password, oauth2_scheme, AuthService
from app.websocket.manager import WebSocketManager, websocket_manager
from app.api.v1.routes import test_cases, teams, environments, attachments

# Pydantic imports
from pydantic import BaseModel, Field, validator, EmailStr

# Environment variables
from dotenv import load_dotenv
import os

# Load environment variables from the .env file in the project root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Print the database URL for debugging (remove in production)
print(f"Database URL: {os.getenv('DATABASE_URL')}")

# Initialize the WebSocket manager
websocket_manager = WebSocketManager()
from app.ai_service import AIService
# Import schemas and models
from app.models import *

# Service imports
from app.auth import AuthService, get_current_user, get_password_hash, verify_password, create_access_token
from app.websocket.manager import WebSocketManager, websocket_manager
from app.ai_service import AIService



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize services
ai_service = AIService()

# WebSocket manager is already initialized in websocket_manager.py
# and imported as websocket_manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting database initialization...")
        
        # Import all models to ensure they are registered with SQLAlchemy
        from app.models.db_models import (
            User, Project, TestCase, TestStep, TestPlan, TestExecution,
            Comment, Team, TeamMember, Environment, Attachment, TestPlanTestCase, ActivityLog
        )
        
        # Create tables in the correct order to avoid foreign key issues
        tables = [
            User.__table__,
            Team.__table__,
            Project.__table__,
            Environment.__table__,  # Moved before TestCase since TestCase might reference it
            TestCase.__table__,
            TestStep.__table__,
            TestPlan.__table__,
            TestPlanTestCase.__table__,
            TestExecution.__table__,  # Depends on TestCase, TestPlan, and Environment
            Comment.__table__,
            TeamMember.__table__,
            Attachment.__table__,
            ActivityLog.__table__
        ]
        
        # Use the sync engine for table operations
        from app.db.session import engine as sync_engine
        
        with sync_engine.connect() as conn:
            # First, disable foreign key constraints
            logger.info("Disabling foreign key constraints...")
            conn.execute(text('SET session_replication_role = "replica";'))
            
            # Get all tables in the database
            result = conn.execute(text(
                """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename;
                """
            ))
            all_tables = [row[0] for row in result]
            
            # Drop all tables in the correct order
            logger.info("Dropping existing tables...")
            for table_name in all_tables:
                try:
                    logger.info(f"Dropping table: {table_name}")
                    conn.execute(text(f'DROP TABLE IF EXISTS \"{table_name}\" CASCADE;'))
                    logger.info(f"Dropped table: {table_name}")
                except Exception as e:
                    logger.error(f"Error dropping table {table_name}: {str(e)}")
                    raise
            
            # Create tables in order
            logger.info("Creating database tables in order...")
            for table in tables:
                try:
                    logger.info(f"Creating table: {table.name}")
                    table.create(conn, checkfirst=True)
                    logger.info(f"Table created: {table.name}")
                except Exception as e:
                    logger.error(f"Error creating table {table.name}: {str(e)}")
                    raise
        
        logger.info("All database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    yield
    logger.info("Application shutdown")

# Configure CORS with specific allowed origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:5175",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://192.168.1.2:5175",  # Network IP for frontend access
    "http://192.168.1.2:5173",  # Additional port for frontend
    "http://localhost:5175"     # Ensure localhost with port 5175 is included
]

# Access token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the main app
app = FastAPI(
    title="IntelliTest AI Automation Platform",
    description="Enterprise-grade AI-powered test automation platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    default_response_class=ORJSONResponse
)

# Add GZip middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware with specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Only allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods for now, can be restricted later
    allow_headers=[
        "*",  # Allow all headers for now to debug CORS issues
    ],
    expose_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Add middleware to add CORS headers to every response
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    origin = request.headers.get('origin')
    if origin in origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRF-Token, Accept, Origin, Accept-Encoding, Accept-Language, Cache-Control, Connection, DNT, Pragma, Referer, User-Agent'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Length, X-Total-Count, Content-Range'
    return response


# CORS is now handled by the CORSMiddleware above

# Create API router with /api prefix to match frontend expectations
api_router = APIRouter(prefix="/api")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and return consistent error responses"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} - "
        f"Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        },
        headers=exc.headers if hasattr(exc, 'headers') else None
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(
        f"Unhandled Exception: {str(exc)} - "
        f"Path: {request.url.path}"
    )
    logger.debug(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# WebSocket endpoint
@app.websocket("/api/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    try:
        await websocket_manager.connect(websocket, user_id)
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
            try:
                message = json.loads(data)
                if message.get("type") == "join_room":
                    await websocket_manager.join_room(user_id, message.get("room_id"))
                elif message.get("type") == "leave_room":
                    await websocket_manager.leave_room(user_id, message.get("room_id"))
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Authentication endpoints
@api_router.post("/auth/register", response_model=dict)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    Request body:
    - email: User's email address
    - password: User's password (min 8 characters)
    - full_name: User's full name
    
    Returns:
    - access_token: JWT token for authentication
    - token_type: Bearer token type
    - user: User information
    """
    request_id = str(uuid.uuid4())
    logger.info(f"[REGISTER-{request_id}] Starting registration for email: {user_data.email}")
    logger.debug(f"[REGISTER-{request_id}] Request URL: {request.url}")
    logger.debug(f"[REGISTER-{request_id}] Request headers: {dict(request.headers)}")
    
    try:
        # Log the request body if possible
        body = await request.body()
        if body:
            logger.debug(f"[REGISTER-{request_id}] Request body: {body.decode()}")
    except Exception as e:
        logger.warning(f"[REGISTER-{request_id}] Could not log request body: {str(e)}")
    
    try:
        # Initialize AuthService with the database session
        logger.info(f"[REGISTER-{request_id}] Initializing AuthService")
        auth_service = AuthService(db)
        
        # Prepare user data dictionary
        logger.debug(f"[REGISTER-{request_id}] Preparing user data")
        user_data_dict = {
            "email": user_data.email,
            "password": user_data.password,
            "full_name": user_data.full_name,
            "role": "tester"  # Default role
        }
        logger.info(f"[REGISTER] User data prepared: {user_data_dict}")
        
        # Validate and create user
        logger.info("[REGISTER] Calling auth_service.create_user")
        user = await auth_service.create_user(user_data_dict)
        logger.info(f"[REGISTER] User created successfully: {user}")
        
        # Create access token
        logger.info("[REGISTER] Creating access token")
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {"sub": str(user["id"]), "email": user["email"], "role": user["role"]}
            logger.info(f"[REGISTER] Token data: {token_data}")
            
            access_token = create_access_token(
                data=token_data,
                expires_delta=access_token_expires
            )
            logger.info("[REGISTER] Access token created successfully")
            
            response_data = {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user
            }
            logger.info(f"[REGISTER] Registration successful for user: {user['email']}")
            return response_data
            
        except Exception as token_error:
            logger.error(f"[REGISTER] Error creating access token: {str(token_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating access token"
            )
        
    except HTTPException as http_exc:
        logger.error(f"[REGISTER] HTTP Exception: {str(http_exc.detail) if hasattr(http_exc, 'detail') else str(http_exc)}")
        logger.debug(f"[REGISTER] HTTP Exception traceback: {traceback.format_exc()}")
        raise http_exc
    except Exception as e:
        error_msg = f"[REGISTER] Unexpected error during registration: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"[REGISTER] Error traceback: {traceback.format_exc()}")
        
        # Provide more detailed error information in development
        error_detail = {
            "detail": "Registration failed due to an unexpected error",
            "error": str(e),
            "type": e.__class__.__name__
        }
        
        # Only include traceback in development
        if os.getenv("ENVIRONMENT", "development").lower() == "development":
            error_detail["traceback"] = traceback.format_exc()
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@api_router.get("/auth/me", response_model=dict)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's information
    
    Requires:
    - Valid JWT token in Authorization header
    
    Returns:
    - User information including id, email, full_name, and role
    """
    try:
        # Get fresh user data from database
        auth_service = AuthService(db)
        user = await auth_service.get_user(current_user["id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user.get("role", "tester"),
            "created_at": user.get("created_at"),
            "updated_at": user.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )

# Project endpoints
@api_router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project
    
    Required fields:
    - name: Project name (1-200 characters)
    - description: Optional project description (max 1000 characters)
    - team_id: Optional ID of the team this project belongs to
    - is_active: Whether the project is active (default: true)
    """
    try:
        # Check if team exists if team_id is provided
        if project_data.team_id:
            team = db.query(Team).filter(Team.id == project_data.team_id).first()
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {project_data.team_id} not found"
                )
        
        # Create project in database
        db_project = Project(
            **project_data.dict(exclude_unset=True),
            created_by=current_user["id"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Create activity log
        create_activity_log(
            db=db,
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            action="created",
            target_type="project",
            target_id=db_project.id,
            target_name=db_project.name,
            description=f"Created project: {db_project.name}"
        )
        
        # Convert to Pydantic model for response
        return Project.model_validate(db_project)
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get a list of projects accessible by the current user
    
    Parameters:
    - skip: Number of projects to skip (for pagination)
    - limit: Maximum number of projects to return (max 100)
    """
    try:
        # Get projects where user is the creator or a team member
        projects = db.query(Project).filter(
            (Project.created_by == current_user["id"]) |
            (Project.team_id.in_(
                db.query(TeamMember.team_id).filter(TeamMember.user_id == current_user["id"])
            ))
        ).offset(skip).limit(min(limit, 100)).all()
        
        return [Project.model_validate(project) for project in projects]
        
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID
    
    Parameters:
    - project_id: The ID of the project to retrieve
    """
    try:
        # Get project with access control
        project = db.query(Project).filter(
            (Project.id == project_id) &
            ((Project.created_by == current_user["id"]) |
             (Project.team_id.in_(
                 db.query(TeamMember.team_id).filter(TeamMember.user_id == current_user["id"])
             )))
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
            
        # Get additional statistics for the project
        test_case_count = db.query(TestCase).filter(TestCase.project_id == project_id).count()
        environment_count = db.query(Environment).filter(Environment.project_id == project_id).count()
        
        # Get last execution time
        last_execution = db.query(TestExecution).filter(
            TestExecution.test_case.has(project_id=project_id)
        ).order_by(TestExecution.started_at.desc()).first()
        
        project_dict = project.__dict__
        project_dict["test_case_count"] = test_case_count
        project_dict["environment_count"] = environment_count
        project_dict["last_execution"] = last_execution.started_at if last_execution else None
        
        return Project.model_validate(project_dict)
        
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )

@api_router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing project
    
    Parameters:
    - project_id: The ID of the project to update
    - project_data: Fields to update (all fields are optional)
    """
    try:
        # Get project with access control
        project = db.query(Project).filter(
            (Project.id == project_id) &
            (Project.created_by == current_user["id"])  # Only project creator can update
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
            
        # Check if team exists if team_id is being updated
        if project_data.team_id is not None and project_data.team_id != project.team_id:
            team = db.query(Team).filter(Team.id == project_data.team_id).first()
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {project_data.team_id} not found"
                )
        
        # Update project fields
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
            
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        # Create activity log
        create_activity_log(
            db=db,
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            action="updated",
            target_type="project",
            target_id=project.id,
            target_name=project.name,
            description=f"Updated project: {project.name}"
        )
        
        return Project.model_validate(project)
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@api_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project
    
    Parameters:
    - project_id: The ID of the project to delete
    """
    try:
        # Get project with access control
        project = db.query(Project).filter(
            (Project.id == project_id) &
            (Project.created_by == current_user["id"])  # Only project creator can delete
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
            
        # Create activity log before deletion
        create_activity_log(
            db=db,
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            action="deleted",
            target_type="project",
            target_id=project.id,
            target_name=project.name,
            description=f"Deleted project: {project.name}"
        )
        
        # Delete the project
        db.delete(project)
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

# Comments endpoints
@api_router.post("/comments", response_model=CommentResponse)
async def create_comment(comment_data: CommentCreate, current_user: dict = Depends(get_current_user)):
    """Create a new comment"""
    db = get_db()
    
    db_comment = DBComment(
        **comment_data.dict(),
        user_id=current_user["id"],
        user_name=current_user["full_name"]
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Convert to Pydantic model for response
    comment = CommentResponse.model_validate(db_comment)
    
    # Create activity log
    create_activity_log(
        db, current_user["id"], current_user["full_name"],
        "commented", "test_case", comment.test_case_id, "",
        f"Added comment on test case"
    )
    
    # Broadcast comment update (if websocket_manager is available)
    if 'websocket_manager' in globals():
        await websocket_manager.broadcast_comment_update(comment.dict())
    
    return comment

@api_router.get("/comments/{test_case_id}", response_model=List[CommentResponse])
async def get_comments(
    test_case_id: str, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a test case"""
    comments = db.query(DBComment).filter(
        DBComment.test_case_id == test_case_id
    ).order_by(DBComment.created_at.asc()).all()
    
    return [CommentResponse.model_validate(comment) for comment in comments]

@api_router.put("/comments/{comment_id}/resolve", response_model=CommentResponse)
async def resolve_comment(
    comment_id: str, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a comment"""
    # Get the comment
    db_comment = db.query(DBComment).filter(
        DBComment.id == comment_id,
        DBComment.user_id == current_user["id"]
    ).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to resolve it"
        )
    
    # Update the comment
    db_comment.resolved = True
    db_comment.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(db_comment)
    
    # Convert to Pydantic model for response
    comment = CommentResponse.model_validate(db_comment)
    
    # Broadcast comment update (if websocket_manager is available)
    if 'websocket_manager' in globals():
        await websocket_manager.broadcast_comment_update(comment.dict())
    
    return comment

# AI endpoints
@api_router.post("/ai/generate-tests", response_model=List[TestCaseResponse])
async def ai_generate_tests(
    request: AITestGenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate test cases using AI"""
    try:
        # Call AI service to generate test cases
        test_cases = await ai_service.generate_test_cases(
            prompt=request.prompt,
            test_type=request.test_type,
            priority=request.priority,
            count=request.count
        )
        
        # Convert to Pydantic models for response
        return [
            TestCaseResponse.model_validate(tc) 
            for tc in test_cases
        ]
        
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test cases: {str(e)}"
        )

@api_router.post("/ai/debug-test", response_model=AIAnalysisResult)
async def ai_debug_test(
    request: AIDebugRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Debug test failure using AI"""
    try:
        # Get the test execution
        execution = db.query(TestExecution).filter(
            TestExecution.id == request.execution_id
        ).first()
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test execution not found"
            )
        
        # Get the test case
        test_case = db.query(DBTestCase).filter(
            DBTestCase.id == execution.test_case_id
        ).first()
        
        if not test_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test case not found"
            )
        
        # Call AI service to debug the test failure
        result = await ai_service.debug_test_failure(
            test_case=test_case,
            error_description=request.error_description,
            logs=request.logs
        )
        
        # Update execution with analysis result
        execution.ai_analysis = result.model_dump()
        db.commit()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error debugging test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to debug test: {str(e)}"
        )

@api_router.post("/ai/prioritize-tests", response_model=List[str])
async def ai_prioritize_tests(
    request: AIPrioritizationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Prioritize test cases using AI"""
    try:
        # Get test cases from database
        test_cases = db.query(DBTestCase).filter(
            DBTestCase.id.in_(request.test_case_ids)
        ).all()
        
        if not test_cases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No test cases found with the provided IDs"
            )
        
        # Call AI service to prioritize test cases
        prioritized_ids = await ai_service.prioritize_test_cases(
            test_cases=test_cases,
            context=request.context
        )
        
        return prioritized_ids
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error prioritizing tests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prioritize tests: {str(e)}"
        )

# Import TestExecution model from db_models
from app.models.db_models import TestExecution as DBTestExecution

# Test Execution endpoints
@api_router.post("/executions", response_model=TestExecutionResponse)
async def create_test_execution(
    execution_data: TestExecutionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new test execution"""
    try:
        # Create new test execution
        db_execution = DBTestExecution(
            **execution_data.dict(),
            executed_by=current_user["id"]
        )
        
        db.add(db_execution)
        db.commit()
        db.refresh(db_execution)
        
        # Convert to Pydantic model for response
        execution = TestExecutionResponse.model_validate(db_execution)
        
        # Broadcast execution update if websocket manager is available
        if 'websocket_manager' in globals():
            await websocket_manager.broadcast_test_execution_update(execution.dict())
        
        return execution
        
    except Exception as e:
        logger.error(f"Error creating test execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test execution: {str(e)}"
        )

@api_router.get("/executions", response_model=List[TestExecutionResponse])
async def get_test_executions(
    test_case_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get test executions"""
    try:
        query = db.query(DBTestExecution)
        
        if test_case_id:
            query = query.filter(DBTestExecution.test_case_id == test_case_id)
        
        # Get most recent 100 executions
        executions = query.order_by(DBTestExecution.created_at.desc()).limit(100).all()
        
        # Convert to Pydantic models for response
        return [
            TestExecutionResponse.model_validate(execution) 
            for execution in executions
        ]
        
    except Exception as e:
        logger.error(f"Error fetching test executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch test executions: {str(e)}"
        )

@api_router.put("/executions/{execution_id}/status", response_model=TestExecutionResponse)
async def update_execution_status(
    execution_id: str,
    status: ExecutionStatus,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update execution status"""
    try:
        # Find the execution
        execution = db.query(DBTestExecution).filter(
            DBTestExecution.id == execution_id
        ).first()
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test execution not found"
            )
        
        # Update status and timestamps
        execution.status = status
        execution.updated_at = datetime.utcnow()
        
        if status == ExecutionStatus.RUNNING:
            execution.started_at = datetime.utcnow()
        elif status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            execution.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(execution)
        
        # Convert to Pydantic model for response
        execution_response = TestExecutionResponse.model_validate(execution)
        
        # Broadcast execution update if websocket manager is available
        if 'websocket_manager' in globals():
            await websocket_manager.broadcast_test_execution_update(
                execution_response.dict()
            )
        
        return execution_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating execution status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update execution status: {str(e)}"
        )

# Import models for dashboard
from app.models.db_models import Project, TestCase as DBTestCase, TestExecution, ActivityLog
from sqlalchemy import or_, and_, func

# Dashboard endpoints
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        # Get user's projects
        projects = db.query(Project).filter(
            or_(
                Project.created_by == current_user["id"],
                Project.team_members.any(current_user["id"])
            )
        ).all()
        
        project_ids = [str(project.id) for project in projects]
        
        if not project_ids:
            return DashboardStats()
        
        # Get statistics
        total_test_cases = db.query(DBTestCase).filter(
            DBTestCase.project_id.in_(project_ids)
        ).count()
        
        # Get executions for pass rate calculation
        executions = db.query(TestExecution).filter(
            TestExecution.test_case.has(DBTestCase.project_id.in_(project_ids))
        ).all()
        
        total_executions = len(executions)
        passed_executions = len([e for e in executions if e.status == "completed"])
        pass_rate = (passed_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate average execution time
        completed_executions = [e for e in executions if e.duration is not None]
        avg_execution_time = sum(e.duration or 0 for e in completed_executions) / len(completed_executions) if completed_executions else 0
        
        # Get active test runs
        active_runs = db.query(TestExecution).filter(
            TestExecution.status == "running"
        ).count()
        
        # Get recent activity
        recent_activity = db.query(ActivityLog).order_by(
            ActivityLog.created_at.desc()
        ).limit(10).all()
        
        # Convert SQLAlchemy models to Pydantic models
        activity_feeds = [
            ActivityFeed(
                id=str(activity.id),
                user_id=activity.user_id,
                user_name=activity.user_name,
                action=activity.action,
                target_type=activity.target_type,
                target_id=activity.target_id,
                target_name=activity.target_name,
                description=activity.description,
                created_at=activity.created_at
            )
            for activity in recent_activity
        ]
        
        return DashboardStats(
            total_test_cases=total_test_cases,
            total_executions=total_executions,
            pass_rate=pass_rate,
            average_execution_time=avg_execution_time,
            active_test_runs=active_runs,
            recent_activity=activity_feeds
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )

@api_router.get("/dashboard/activity", response_model=List[ActivityFeed])
async def get_activity_feed(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get activity feed"""
    try:
        activities = db.query(ActivityLog).order_by(
            ActivityLog.created_at.desc()
        ).limit(limit).all()
        
        return [
            ActivityFeed(
                id=str(activity.id),
                user_id=activity.user_id,
                user_name=activity.user_name,
                action=activity.action,
                target_type=activity.target_type,
                target_id=activity.target_id,
                target_name=activity.target_name,
                description=activity.description,
                created_at=activity.created_at
            )
            for activity in activities
        ]
    except Exception as e:
        logger.error(f"Error getting activity feed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity feed"
        )

# Utility functions
async def create_activity_log(db, user_id: str, user_name: str, action: str, target_type: str, target_id: str, target_name: str, description: str):
    """Create activity log entry"""
    activity = ActivityFeed(
        user_id=user_id,
        user_name=user_name,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        description=description
    )
    
    await db.activity_feed.insert_one(activity.dict())
    
    # Broadcast dashboard update
    await websocket_manager.broadcast_dashboard_update({
        "type": "activity_update",
        "activity": activity.dict()
    })

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Include API routers with the correct prefix
# Note: We're using a simplified approach to avoid import errors
try:
    logger.info("Initializing API routers...")
    
    # Include routers with /api prefix (no /v1 in the path)
    # The individual route files will handle their own sub-paths
    
    # Include the main API router that has the /api prefix already set
    app.include_router(api_router)
    
    # Include other routers as they become available
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(projects.router, prefix="/v1/projects", tags=["Projects"])
    app.include_router(test_cases.router, prefix="/api/v1/test-cases", tags=["Test Cases"])
    
    logger.info("API routers initialized successfully")
except Exception as e:
    logger.error(f"Error initializing API routers: {str(e)}")
    logger.debug(traceback.format_exc())
    # Don't raise - let the app continue with the routes that did load

# Root endpoint for backward compatibility
@app.get("/", tags=["Health"])
async def root() -> dict:
    """
    Root endpoint for health checks and basic API information.
    
    Returns:
        dict: API status and version information
    """
    return {
        "message": "Welcome to IntelliTest API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint to verify the API is running and can connect to the database.
    
    Returns:
        dict: Health status and database connection status
    """
    db_ok = False
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db_ok = True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        logger.debug(traceback.format_exc())
    finally:
        db.close()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Run the application
    uvicorn.run(
        "server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8001)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info"),
    )
