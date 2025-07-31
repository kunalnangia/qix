import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
env_path = str(Path(__file__).parent / '.env')
load_dotenv(env_path)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def get_database_url():
    """Get database URL from environment variables"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    return db_url

def get_expected_tables():
    """Return a list of expected table names"""
    return [
        'users', 'projects', 'test_cases', 'test_steps',
        'test_plans', 'test_executions', 'comments', 'teams',
        'team_members', 'environments', 'attachments',
        'activity_logs', 'test_plan_test_cases'
    ]

def create_all_tables(engine):
    """Create all tables based on SQLAlchemy models"""
    print("\n🔄 Creating all tables...")
    try:
        from app.db.base import Base
        from app.models.db_models import (
            User, Project, TestCase, TestStep, TestPlan, TestExecution,
            Comment, Team, TeamMember, Environment, Attachment, ActivityLog,
            TestPlanTestCase
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def drop_all_tables(engine):
    """Drop all tables in the database"""
    print("\n⚠️  Dropping all tables...")
    try:
        # Get the metadata
        metadata = MetaData()
        
        # Reflect all tables
        metadata.reflect(bind=engine)
        
        # Drop all tables
        metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error dropping tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_missing_tables(engine):
    """Check which expected tables are missing"""
    print("\n🔍 Checking for missing tables...")
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(get_expected_tables())
    
    missing_tables = expected_tables - existing_tables
    extra_tables = existing_tables - expected_tables
    
    print(f"✅ Found {len(existing_tables)} existing tables")
    
    if missing_tables:
        print(f"\n❌ Missing {len(missing_tables)} tables:")
        for i, table in enumerate(sorted(missing_tables), 1):
            print(f"{i}. {table}")
    else:
        print("\n✅ All expected tables exist")
    
    if extra_tables:
        print(f"\n⚠️  Found {len(extra_tables)} unexpected tables:")
        for i, table in enumerate(sorted(extra_tables), 1):
            print(f"{i}. {table}")
    
    return list(missing_tables)

def sync_database():
    """Synchronize database schema with models"""
    try:
        # Get database URL and create engine
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        print_header("database synchronization")
        
        # Check current state
        missing_tables = check_missing_tables(engine)
        
        if not missing_tables:
            print("\n✅ Database schema is up to date")
            return True
        
        # Ask for confirmation
        print("\n⚠️  This will modify the database structure.")
        confirm = input("Do you want to synchronize the database? (y/n): ")
        
        if confirm.lower() != 'y':
            print("\n❌ Operation cancelled by user")
            return False
        
        # Drop existing tables if needed
        if not drop_all_tables(engine):
            return False
        
        # Create all tables
        if not create_all_tables(engine):
            return False
        
        # Verify final state
        missing_tables = check_missing_tables(engine)
        if missing_tables:
            print(f"\n❌ Failed to create all tables: {', '.join(missing_tables)}")
            return False
        
        print("\n✨ Database synchronization completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    if sync_database():
        sys.exit(0)
    else:
        sys.exit(1)
