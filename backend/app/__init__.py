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

# Initialize the database when the package is imported
# This ensures tables are created when the application starts
init_db()

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
