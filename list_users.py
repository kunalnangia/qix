import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

def list_users():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return
    
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        # Connect to the database
        with engine.connect() as connection:
            # Query to list all users with their details
            result = connection.execute(text("""
                SELECT id, email, full_name, role, is_active, created_at, updated_at
                FROM users
                ORDER BY created_at DESC;
            """))
            users = result.fetchall()
            
            if not users:
                print("ℹ️ No users found in the database.")
                return
            
            # Print table header
            print(f"\n{'ID':<38} | {'Email':<25} | {'Name':<15} | {'Role':<10} | {'Active':<6} | {'Created At'}")
            print("-" * 120)
            
            # Print each user's details
            for user in users:
                user_id = user[0]
                email = user[1] or 'N/A'
                full_name = user[2] or 'N/A'
                role = user[3] or 'user'
                is_active = str(bool(user[4]))
                created_at = user[5].strftime('%Y-%m-%d %H:%M') if user[5] else 'N/A'
                
                # Truncate long fields for display
                if len(email) > 22:
                    email = email[:19] + "..."
                if len(full_name) > 12:
                    full_name = full_name[:9] + "..."
                
                print(f"{user_id} | {email:<25} | {full_name:<15} | {role:<10} | {is_active:<6} | {created_at}")
            
            # Print summary
            print(f"\nTotal users: {len(users)}")
                
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Provide more specific error messages
        if "relation " in str(e) and " does not exist" in str(e):
            print("\n🔧 The 'users' table doesn't exist yet. You may need to run database migrations first.")
        elif "Connection refused" in str(e):
            print("\n🔧 Could not connect to the database. Please check:")
            print("1. Is the database server running?")
            print("2. Are the connection details in .env correct?")
            print(f"3. Can you connect using: psql {DATABASE_URL}")
        elif "authentication failed" in str(e).lower():
            print("\n🔧 Authentication failed. Please check:")
            print("1. Is the username and password correct in the DATABASE_URL?")
            print("2. Does the user have permission to access the database?")

if __name__ == "__main__":
    print("🔍 Checking for existing users in the database...")
    list_users()
