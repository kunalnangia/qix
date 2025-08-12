import os
import bcrypt
import uuid
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def register_user(email: str, password: str, full_name: str, role: str = "user"):
    """Register a new user in the database."""
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Connect to the database
        with engine.connect() as connection:
            # Check if user already exists
            result = connection.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            
            if result.fetchone() is not None:
                print(f"❌ User with email {email} already exists.")
                return False
            
            # First, let's check the users table schema
            result = connection.execute(
                text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users';
                """)
            )
            print("\nUsers table schema:")
            print("-" * 30)
            for col in result.fetchall():
                print(f"{col[0]} ({col[1]})")
            
            # Generate a new UUID for the user
            user_id = str(uuid.uuid4())
            print(f"\nGenerated user ID: {user_id}")
            
            # Now try to insert the user with the generated UUID
            print("Attempting to insert user...")
            result = connection.execute(
                text("""
                    INSERT INTO users (id, email, hashed_password, full_name, role, is_active)
                    VALUES (:id, :email, :hashed_password, :full_name, :role, :is_active)
                    RETURNING id, email, full_name, role, is_active, created_at
                """),
                {
                    "id": user_id,
                    "email": email,
                    "hashed_password": hashed_password,
                    "full_name": full_name,
                    "role": role,
                    "is_active": True
                }
            )
            
            # Commit the transaction
            connection.commit()
            
            # Get the created user
            user = result.fetchone()
            
            print("✅ User registered successfully:")
            print(f"ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Full Name: {user[2]}")
            print(f"Role: {user[3]}")
            print(f"Active: {user[4]}")
            print(f"Created At: {user[5]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        return False

if __name__ == "__main__":
    import getpass
    
    print("👤 Register a new user")
    print("-" * 30)
    
    # Get user input
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ").strip()
    full_name = input("Full Name: ").strip()
    
    # Register the user
    if register_user(email, password, full_name):
        print("\n✅ Registration successful!")
    else:
        print("\n❌ Registration failed. Please check the error message above.")
