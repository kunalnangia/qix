from .db.session import SessionLocal, engine, get_db, AsyncSessionLocal, init_db, Base
from .models.db_models import *
from .core.config import settings
from .auth.security import AuthService, get_current_user, create_access_token, get_password_hash, verify_password

__all__ = [
    'SessionLocal',
    'AsyncSessionLocal', 
    'engine',
    'get_db',
    'init_db',
    'Base',
    'settings',
    # Auth
    'AuthService',
    'get_current_user',
    'create_access_token',
    'get_password_hash',
    'verify_password',
    # Models
    'User',
    'Team',
    'TeamMember',
    'Project',
    'Environment',
    'TestCase',
    'TestStep',
    'TestPlan',
    'TestExecution',
    'Comment',
    'Attachment',
    # Enums
    'TestType',
    'Priority',
    'Status',
    'ExecutionStatus',
    'CommentType'
]

# Initialize database tables
Base.metadata.create_all(bind=engine)