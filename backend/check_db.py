import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def check_db_connection():
    try:
        # Load environment variables
        env_path = str(Path(__file__).parent / '.env')
        load_dotenv(env_path)
        
        # Get database URL from environment or use default
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print_header("database connection test")
        print(f"🔍 Connecting to: {db_url}")
        
        # Create engine and test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Test basic connection
            version = conn.execute(text("SELECT version()")).scalar()
            print(f"✅ Connected to: {version}")
            
            # Get database info
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            db_user = conn.execute(text("SELECT current_user")).scalar()
            db_schema = conn.execute(text("SELECT current_schema()")).scalar()
            
            print(f"\n📊 Database: {db_name}")
            print(f"👤 User: {db_user}")
            print(f"🏷️  Schema: {db_schema}")
            
            # List all schemas
            print("\n📋 Available schemas:")
            schemas = conn.execute(text("""
                SELECT nspname 
                FROM pg_catalog.pg_namespace 
                WHERE nspname NOT LIKE 'pg_%' AND nspname != 'information_schema'
                ORDER BY nspname
            """))
            
            for schema in schemas:
                print(f"- {schema[0]}")
            
            # List all tables in public schema
            print("\n📋 Tables in public schema:")
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            table_list = [row[0] for row in tables]
            for table in table_list:
                print(f"- {table}")
            
            # Check if all expected tables exist
            expected_tables = {
                'users', 'projects', 'test_cases', 'test_steps',
                'test_plans', 'test_executions', 'comments', 'teams',
                'team_members', 'environments', 'attachments',
                'activity_logs', 'test_plan_test_cases'
            }
            
            missing_tables = expected_tables - set(table_list)
            if missing_tables:
                print("\n❌ Missing tables:")
                for table in sorted(missing_tables):
                    print(f"- {table}")
            
            # Get table row counts
            print("\n📊 Table row counts:")
            for table in table_list:
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM \"{table}\"")).scalar()
                    print(f"- {table}: {count} rows")
                except Exception as e:
                    print(f"- {table}: Error - {str(e)}")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"\n❌ Database error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_orm_models():
    try:
        print_header("sqlalchemy model test")
        
        # Test importing all models
        from app.db.base import Base
        from app.models.db_models import (
            User, Project, TestCase, TestStep, TestPlan, TestExecution,
            Comment, Team, TeamMember, Environment, Attachment, ActivityLog,
            TestPlanTestCase
        )
        
        print("✅ Successfully imported all SQLAlchemy models")
        
        # Test model relationships
        print("\n🔍 Testing model relationships...")
        print(f"- User model has {len(User.__table__.columns)} columns")
        print(f"- Project model has {len(Project.__table__.columns)} columns")
        print(f"- TestCase model has {len(TestCase.__table__.columns)} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ORM models: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test database connection
    connection_ok = check_db_connection()
    
    # Test ORM model imports
    models_ok = test_orm_models()
    
    print_header("test summary")
    if connection_ok and models_ok:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. See above for details.")
