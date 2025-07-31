import os
import sys
import asyncio
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

def drop_all_tables(engine):
    """Drop all tables in the database"""
    print("🗑️  Dropping all tables...")
    
    # Get a list of all tables in the database
    with engine.connect() as conn:
        # Disable foreign key checks temporarily
        conn.execute(text('SET session_replication_role = \'replica\';'))
        
        # Get all table names
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        "))
        tables = [row[0] for row in result]
        
        # Drop all tables
        for table in tables:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS \"{table}\" CASCADE;'))
                print(f"  - Dropped table: {table}")
            except Exception as e:
                print(f"  - Error dropping table {table}: {str(e)}")
        
        # Re-enable foreign key checks
        conn.execute(text('SET session_replication_role = \'origin\';'))
        conn.commit()
    
    print("✅ All tables dropped successfully!")

def create_tables(engine):
    """Create all tables based on SQLAlchemy models"""
    print("\n🔄 Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables(engine):
    """Verify that all expected tables exist in the database"""
    print("\n🔍 Verifying database schema...")
    
    try:
        with engine.connect() as conn:
            # Get list of existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            â€´´´))
            
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
            extra_tables = existing_tables - expected_tables
            
            if missing_tables:
                print("\n❌ Missing tables:")
                for table in sorted(missing_tables):
                    print(f"- {table}")
            else:
                print("\n✅ All expected tables exist in the database")
                
            if extra_tables:
                print("\n⚠️  Extra tables found (not in models):")
                for table in sorted(extra_tables):
                    print(f"- {table}")
            
            return len(missing_tables) == 0
                
    except Exception as e:
        print(f"❌ Error verifying tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Get database URL from environment variables
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Database URL: {db_url}")
    
    # Create engine
    engine = create_engine(db_url)
    
    # Drop all existing tables
    drop_all_tables(engine)
    
    # Create all tables
    if not create_tables(engine):
        return False
    
    # Verify tables were created
    if not verify_tables(engine):
        return False
    
    print("\n✨ Database synchronization complete!")
    return True

if __name__ == "__main__":
    print("🚀 Starting database synchronization...")
    if main():
        print("\n✅ Database synchronization completed successfully!")
        print("\nYou can now start the FastAPI application with:")
        print("uvicorn app.main:app --reload --port 8001 --host 0.0.0.0")
    else:
        print("\n❌ Database synchronization failed. Please check the error messages above.")
