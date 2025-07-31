import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.db_models import User
from app.auth.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@gmail.com").first()
        if existing_user:
            print("Test user already exists with ID:", existing_user.id)
            return
        
        # Create test user
        hashed_password = get_password_hash("test1234")
        test_user = User(
            email="test@gmail.com",
            full_name="Test User",
            hashed_password=hashed_password,
            role="tester"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Test user created successfully with ID: {test_user.id}")
        
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
