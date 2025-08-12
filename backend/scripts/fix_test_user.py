from app.db.session import SessionLocal
from app.models.db_models import User
from app.auth.security import get_password_hash

def fix_test_user():
    db = SessionLocal()
    try:
        # Find or create test user
        test_user = db.query(User).filter(User.email == "test@gmail.com").first()
        
        if not test_user:
            # Create test user if it doesn't exist
            test_user = User(
                email="test@gmail.com",
                full_name="Test User",
                hashed_password=get_password_hash("test123"),
                role="tester"
            )
            db.add(test_user)
            print("Created new test user")
        else:
            # Update existing user's password
            test_user.hashed_password = get_password_hash("test123")
            print("Updated existing test user's password")
        
        db.commit()
        db.refresh(test_user)
        
        print("\nTest user details:")
        print(f"Email: {test_user.email}")
        print(f"Name: {test_user.full_name}")
        print(f"Role: {test_user.role}")
        print(f"User ID: {test_user.id}")
        
        return True
        
    except Exception as e:
        print(f"Error fixing test user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if fix_test_user():
        print("\nTest user is ready with password 'test123'")
        print("You can now try logging in with:")
        print("Email: test@gmail.com")
        print("Password: test123")
