import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Database connection parameters
    db_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'port': '5432',
        'connect_timeout': 5
    }
    
    test_email = os.getenv("TEST_USER_EMAIL", "test@example.com")
    
    print("Checking test user in database...")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if test user exists
        cursor.execute(
            "SELECT id, email, is_active FROM users WHERE email = %s",
            (test_email,)
        )
        
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found: {user[1]} (ID: {user[0]}, Active: {user[2]})")
        else:
            print(f"❌ User not found: {test_email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
