import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
env_path = str(Path(__file__).parent / '.env')
load_dotenv(env_path)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def test_direct_connection():
    try:
        print_header("direct database connection test")
        
        # Get database URL from environment
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"🔍 Connecting to: {db_url}")
        
        # Create engine with echo=True for SQL output
        engine = create_engine(db_url, echo=True)
        
        # Test connection
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Basic query result: {result.scalar()}")
            
            # Get database info
            db_info = conn.execute(text("""
                SELECT 
                    current_database() as db_name,
                    current_user as db_user,
                    current_schema() as db_schema,
                    version() as db_version
            """)).fetchone()
            
            print(f"\n📊 Database Info:")
            print(f"- Name: {db_info.db_name}")
            print(f"- User: {db_info.db_user}")
            print(f"- Schema: {db_info.db_schema}")
            print(f"- Version: {db_info.db_version}")
            
            # List all tables
            print("\n📋 Listing all tables:")
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            table_list = [row[0] for row in tables]
            for table in table_list:
                print(f"- {table}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_orm_connection():
    try:
        print_header("sqlalchemy orm test")
        
        # Import models
        from app.db.base import Base
        from app.models.db_models import (
            User, Project, TestCase, TestStep, TestPlan, TestExecution,
            Comment, Team, TeamMember, Environment, Attachment, ActivityLog,
            TestPlanTestCase
        )
        
        # Get database URL from environment
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"🔍 Connecting to: {db_url}")
        
        # Create engine and session
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Test ORM query
            print("\n🔍 Testing ORM models...")
            
            # Test User model
            print("\n👤 Testing User model:")
            user_count = db.query(User).count()
            print(f"- Found {user_count} users in the database")
            
            # Test Project model
            print("\n📂 Testing Project model:")
            project_count = db.query(Project).count()
            print(f"- Found {project_count} projects in the database")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting database tests...")
    
    # Test direct connection
    connection_ok = test_direct_connection()
    
    # Test ORM connection if direct connection was successful
    orm_ok = False
    if connection_ok:
        orm_ok = test_orm_connection()
    
    print_header("test summary")
    if connection_ok and orm_ok:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. See above for details.")
