from sqlalchemy.ext.declarative import declarative_base

# Create a base class for our models
Base = declarative_base()

# Import all SQLAlchemy models
# Import SQLAlchemy models from the app.models.db_models
from app.models.db_models import (
    User, Project, TestStep, TestCase, TestPlan, 
    TestExecution, Comment, Team, TeamMember, 
    Environment, Attachment, TestPlanTestCase,
    WebSocketMessage as SQLWebSocketMessage,
    NotificationMessage as SQLNotificationMessage
)

# Import Pydantic models
from ..models import (
    WebSocketMessage, NotificationMessage
)
# Import WebSocket manager
from .websocket_manager import WebSocketManager, websocket_manager

# This makes these available when importing from models
__all__ = [
    # Base
    'Base',
    
    # SQLAlchemy models
    'User',
    'Project',
    'TestCase',
    'TestStep',
    'TestPlan',
    'TestExecution',
    'Comment',
    'Team',
    'TeamMember',
    'Environment',
    'Attachment',
    'TestPlanTestCase',
    'SQLWebSocketMessage',
    'SQLNotificationMessage',
    
    # Pydantic models
    'WebSocketMessage',
    'NotificationMessage',
    
    # WebSocket
    'WebSocketManager',
    'websocket_manager'
]