from .app.db.session import SessionLocal, engine, get_db, AsyncSessionLocal, init_db, Base
from .app.models.db_models import *
from .app.core.config import settings
from .app.auth.security import get_current_user, create_access_token, get_password_hash, verify_password

# AuthService seems to be defined in a different place, let's omit it for now to fix the path issue
# from .auth.security import AuthService

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

# The application startup logic should handle database creation.
# This line can cause issues, especially during testing.
# Base.metadata.create_all(bind=engine)