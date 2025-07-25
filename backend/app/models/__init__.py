# Export Base from sqlalchemy.ext.declarative
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import models after Base is defined to avoid circular imports
from .db_models import (
    User, Project, TestStep, TestCase, TestPlan,
    TestExecution, Comment, Team, TeamMember,
    Environment, Attachment, TestPlanTestCase
)

# Import WebSocket related models from schemas
from ..schemas.websocket import WebSocketMessage, NotificationMessage

__all__ = [
    'Base',
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
    'WebSocketMessage',
    'NotificationMessage'
]
