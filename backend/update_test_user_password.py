from app.db.session import SessionLocal
from app.models.db_models import User
from passlib.context import CryptContext

def update_test_user_password():
    db = SessionLocal()
    try:
        # Find the test user
        test_user = db.query(User).filter(User.email == "test@gmail.com").first()
        if not test_user:
            print("Test user not found")
            return
        
        # Create a password hash
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("test123")
        
        # Update the user's password
        test_user.hashed_password = hashed_password
        db.commit()
        
        print(f"Password updated for user: {test_user.email}")
        print(f"New hashed password: {hashed_password}")
        
    except Exception as e:
        print(f"Error updating password: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_test_user_password()
