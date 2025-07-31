import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_test_user():
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
    
    print("=" * 80)
    print("VERIFYING TEST USER IN DATABASE")
    print("=" * 80)
    print(f"Database: {db_params['host']}")
    print(f"Looking for user: {test_email}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        users_table_exists = cursor.fetchone()[0]
        
        if not users_table_exists:
            print("\n❌ Users table does not exist in the database!")
            return False
            
        # Check if test user exists
        cursor.execute(
            "SELECT id, email, is_active, is_superuser FROM users WHERE email = %s",
            (test_email,)
        )
        user = cursor.fetchone()
        
        if user:
            print("\n✅ Test user found in database:")
            print(f"ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Active: {user[2]}")
            print(f"Superuser: {user[3]}")
            
            # Check if user has any login records
            cursor.execute("""
                SELECT COUNT(*) FROM login_history 
                WHERE user_id = %s
            """, (user[0],))
            login_count = cursor.fetchone()[0]
            print(f"\nLogin attempts: {login_count}")
            
            if login_count > 0:
                cursor.execute("""
                    SELECT login_time, status, ip_address 
                    FROM login_history 
                    WHERE user_id = %s 
                    ORDER BY login_time DESC 
                    LIMIT 5
                """, (user[0],))
                
                print("\nRecent login attempts:")
                for attempt in cursor.fetchall():
                    print(f"- {attempt[0]} | {attempt[1]} | {attempt[2] or 'N/A'}")
            
            return True
            
        else:
            print(f"\n❌ Test user '{test_email}' not found in the database!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error checking test user: {str(e)}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = verify_test_user()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST USER VERIFICATION COMPLETED")
    else:
        print("❌ TEST USER VERIFICATION FAILED")
    print("=" * 80)
