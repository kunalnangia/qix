import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings directly to get database URL
from app.core.config import settings

def test_connection():
    print("🔍 Testing database connection...")
    print(f"Database URL: {settings.DATABASE_URI}")
    
    try:
        # Create a synchronous engine for testing
        engine = create_engine(
            settings.DATABASE_URI,
            echo=True
        )
        
        # Test the connection
        with engine.connect() as conn:
            # Get database version
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"\n✅ Successfully connected to database!")
            print(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            
            tables = result.fetchall()
            print("\nTables in the database:")
            for table in sorted(tables):
                print(f"- {table[0]}")
                
    except Exception as e:
        print(f"\n❌ Error connecting to database: {str(e)}")
        return False
    
    return True

def check_test_user():
    print("\n🔍 Checking for test user...")
    try:
        engine = create_engine(settings.DATABASE_URI)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if users table exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            
            if not result.scalar():
                print("❌ Users table does not exist in the database")
                return False
                
            # Check for test user
            result = db.execute(text("""
                SELECT id, email, full_name, role, is_active 
                FROM users 
                WHERE email = 'test@gmail.com';
            """))
            
            user = result.fetchone()
            if user:
                print(f"✅ Test user found:")
                print(f"   ID: {user[0]}")
                print(f"   Email: {user[1]}")
                print(f"   Name: {user[2]}")
                print(f"   Role: {user[3]}")
                print(f"   Active: {user[4]}")
                return True
            else:
                print("❌ Test user (test@gmail.com) not found in the database")
                return False
                
        except Exception as e:
            print(f"❌ Error checking for test user: {str(e)}")
            return False
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating database session: {str(e)}")
        return False

def create_test_user():
    print("\n🔧 Creating test user...")
    try:
        from app.core.security import get_password_hash
        from app.models.db_models import User
        
        engine = create_engine(settings.DATABASE_URI)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if test user already exists
            result = db.execute(text("""
                SELECT id FROM users WHERE email = 'test@gmail.com';
            """))
            
            if result.fetchone():
                print("ℹ️ Test user already exists")
                return True
                
            # Create test user
            from uuid import uuid4
            from datetime import datetime
            
            user = User(
                id=str(uuid4()),
                email="test@gmail.com",
                hashed_password=get_password_hash("test1234"),
                full_name="Test User",
                is_active=True,
                role="tester",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            print("✅ Test user created successfully!")
            print(f"   Email: test@gmail.com")
            print(f"   Password: test1234")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating test user: {str(e)}")
            return False
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Database Verification Tool ===")
    
    # Test database connection
    if not test_connection():
        print("\n❌ Database connection failed. Please check your configuration.")
        sys.exit(1)
    
    # Check for test user
    if not check_test_user():
        print("\nWould you like to create a test user? (y/n) ", end="")
        if input().lower() == 'y':
            if create_test_user():
                print("\n✅ Test user created successfully!")
                print("You can now log in with:")
                print("  Email: test@gmail.com")
                print("  Password: test1234")
            else:
                print("\n❌ Failed to create test user.")
        else:
            print("\nTest user not created.")
    
    print("\n=== Verification Complete ===")
