import os
import sys
import psycopg2
from datetime import datetime, timezone
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_test_user():
    # Database connection parameters
    db_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'port': '5432',
        'connect_timeout': 5
    }
    
    # Test user details
    test_user = {
        'email': 'test@example.com',
        'password': 'test1234',
        'full_name': 'Test User',
        'is_active': True,
        'is_superuser': False
    }
    
    print("Attempting to add test user...")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (test_user['email'],)
        )
        
        if cursor.fetchone():
            print(f"❌ User already exists: {test_user['email']}")
            return False
        
        # Hash the password
        hashed_password = pwd_context.hash(test_user['password'])
        
        # Insert the test user
        cursor.execute("""
            INSERT INTO users (
                email, 
                hashed_password, 
                full_name, 
                is_active, 
                is_superuser,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            test_user['email'],
            hashed_password,
            test_user['full_name'],
            test_user['is_active'],
            test_user['is_superuser'],
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ))
        
        user_id = cursor.fetchone()[0]
        print(f"✅ Successfully added test user with ID: {user_id}")
        print(f"Email: {test_user['email']}")
        print(f"Password: {test_user['password']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding test user: {str(e)}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_test_user()
