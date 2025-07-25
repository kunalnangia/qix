"""Manually fix import issues in server.py."""
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def fix_server_imports():
    """Manually fix import statements in server.py."""
    server_path = os.path.join(project_root, 'backend', 'server.py')
    
    # Read the current content
    with open(server_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the first non-import line
    first_non_import = 0
    for i, line in enumerate(lines):
        if not line.startswith(('import ', 'from ')) and line.strip() != '':
            first_non_import = i
            break
    
    # Define the new imports to add
    new_imports = [
        'import os\n',
        'import sys\n',
        'from datetime import datetime, timedelta\n',
        'from typing import List, Dict, Any, Optional, Set, Union\n',
        'from contextlib import asynccontextmanager\n',
        'from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status, Request, BackgroundTasks\n',
        'from fastapi.middleware.cors import CORSMiddleware\n',
        'from fastapi.responses import JSONResponse\n',
        'from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials\n',
        'from sqlalchemy.orm import Session\n',
        'from sqlalchemy.exc import SQLAlchemyError\n',
        'from pydantic import BaseModel, Field, validator, EmailStr\n',
        'from dotenv import load_dotenv\n',
        '\n',
        '# Local imports\n',
        'from backend.database_sqlite import SessionLocal, engine, Base, get_db, init_db\n',
        'from backend import models\n',
        'from backend.websocket_manager import WebSocketManager, websocket_manager\n',
        'from backend.ai_service import AIService\n',
        'from backend.auth import AuthService, create_access_token, get_password_hash, get_current_user\n',
        '\n',
    ]
    
    # Replace the first part of the file with our new imports
    updated_lines = new_imports + lines[first_non_import:]
    
    # Write the updated content back to the file
    with open(server_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("✓ Updated imports in server.py with correct absolute imports")

if __name__ == "__main__":
    fix_server_imports()
