import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
env_path = str(Path(__file__).parent / '.env')
load_dotenv(env_path)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.db_models import (
    User, Project, TestCase, TestStep, TestPlan, TestExecution,
    Comment, Team, TeamMember, Environment, Attachment, ActivityLog,
    TestPlanTestCase
)

def create_tables():
    """Create all database tables based on SQLAlchemy models"""
    # Get database URL from environment variables
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Connecting to database: {db_url}")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Create all tables
        print("🔄 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """Verify that all expected tables exist in the database"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Get list of existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = {row[0] for row in result.fetchall()}
            
            # Expected tables from our models
            expected_tables = {
                'users', 'projects', 'test_cases', 'test_steps',
                'test_plans', 'test_executions', 'comments', 'teams',
                'team_members', 'environments', 'attachments',
                'activity_logs', 'test_plan_test_cases'
            }
            
            # Find missing tables
            missing_tables = expected_tables - existing_tables
            
            if missing_tables:
                print("\n❌ Missing tables:")
                for table in sorted(missing_tables):
                    print(f"- {table}")
                return False
            else:
                print("\n✅ All expected tables exist in the database")
                return True
                
    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database initialization...")
    
    # Create tables
    if create_tables():
        # Verify tables were created
        verify_tables()
    
    print("\nDatabase initialization complete!")
    print("\nYou can now start the FastAPI application with:")
    print("uvicorn app.main:app --reload --port 8001 --host 0.0.0.0")
