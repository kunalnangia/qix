from app.db.session import SessionLocal
from app.models.db_models import User

def check_test_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'test@gmail.com').first()
        if user:
            print(f"User found: {user.email}")
            print(f"Password hash: {user.hashed_password}")
            print(f"User ID: {user.id}")
            print(f"Full Name: {user.full_name}")
            print(f"Role: {user.role}")
        else:
            print("Test user not found in the database")
    except Exception as e:
        print(f"Error checking test user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_test_user()
