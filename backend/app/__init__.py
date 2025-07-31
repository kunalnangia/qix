"""
IntelliTest AI Automation Platform - Main Application Package

This package contains the core functionality of the IntelliTest AI Automation Platform.
"""

# Import key components to make them available at the package level
from .main import app
from .db.session import SessionLocal, engine, init_db
from .models import *
from .auth.security import (
    get_current_user,
    create_access_token,
    get_password_hash,
    verify_password,
    AuthService
)

# Note: Database initialization is now handled in the FastAPI lifespan event
# This prevents issues with async/await and ensures proper initialization order

__all__ = [
    'app',
    'SessionLocal',
    'engine',
    'get_current_user',
    'create_access_token',
    'get_password_hash',
    'verify_password',
    'AuthService',
    'init_db'
]
