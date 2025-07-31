import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def test_imports():
    """Test importing all required modules"""
    print_header("testing imports")
    
    try:
        # Test core imports
        print("🔍 Testing core imports...")
        from app.db.base import Base
        from app.db.session import engine, SessionLocal
        print("✅ Core database imports successful")
        
        # Test model imports
        print("\n🔍 Testing model imports...")
        from app.models.db_models import (
            User, Project, TestCase, TestStep, TestPlan, TestExecution,
            Comment, Team, TeamMember, Environment, Attachment, ActivityLog,
            TestPlanTestCase
        )
        print("✅ Model imports successful")
        
        # Test schema imports
        print("\n🔍 Testing schema imports...")
        from app.schemas.user import UserCreate, UserInDB, UserUpdate, UserInDBBase
        from app.schemas.token import Token, TokenPayload
        from app.schemas.msg import Msg
        print("✅ Schema imports successful")
        
        # Test API imports
        print("\n🔍 Testing API imports...")
        from app.api.api_v1.api import api_router
        from app.core.config import settings
        print("✅ API imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection using SQLAlchemy"""
    print_header("testing database connection")
    
    try:
        from sqlalchemy import text
        from app.db.session import engine, SessionLocal
        
        # Test engine connection
        print("🔍 Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Database connection test: {result.scalar()}")
            
            # Test schema
            print("\n🔍 Checking database schema...")
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            table_list = [row[0] for row in tables]
            print(f"Found {len(table_list)} tables in the database")
            
            # Check for required tables
            required_tables = {
                'users', 'projects', 'test_cases', 'test_steps',
                'test_plans', 'test_executions', 'comments', 'teams',
                'team_members', 'environments', 'attachments',
                'activity_logs', 'test_plan_test_cases'
            }
            
            missing_tables = required_tables - set(table_list)
            if missing_tables:
                print("\n❌ Missing required tables:")
                for table in sorted(missing_tables):
                    print(f"- {table}")
            else:
                print("\n✅ All required tables exist")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_app_initialization():
    """Test FastAPI app initialization"""
    print_header("testing fastapi app initialization")
    
    try:
        from app.main import app
        
        # Check if app is a FastAPI instance
        if not isinstance(app, FastAPI):
            print("❌ app is not a FastAPI instance")
            return False
            
        # Check routes
        print("\n🔍 Checking registered routes...")
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', [])
                routes.append((route.path, ', '.join(methods) if methods else 'N/A'))
        
        # Print first 10 routes
        print("\n📋 Registered routes (first 10):")
        for path, methods in routes[:10]:
            print(f"- {path} [{methods}]")
            
        if len(routes) > 10:
            print(f"... and {len(routes) - 10} more routes")
            
        return True
        
    except Exception as e:
        print(f"❌ App initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Load environment variables
    env_path = str(Path(__file__).parent / '.env')
    load_dotenv(env_path)
    
    print("🚀 Starting FastAPI application tests...")
    
    # Run tests
    tests = [
        ("Import Tests", test_imports),
        ("Database Connection", test_database_connection),
        ("App Initialization", test_app_initialization)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*40} {name} {'='*(40-len(name))}")
        success = test_func()
        results.append((name, success))
    
    # Print summary
    print_header("test summary")
    all_passed = all(success for _, success in results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
    
    if all_passed:
        print("\n✨ All tests passed successfully!")
        print("\nYou can start the application with:")
        print("uvicorn app.main:app --reload --port 8001 --host 0.0.0.0")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
