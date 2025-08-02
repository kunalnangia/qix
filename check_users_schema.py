import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def check_users_schema():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Connect to the database
        with engine.connect() as connection:
            # Get column information for users table
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users';
            """))
            
            columns = result.fetchall()
            
            if not columns:
                print("❌ Users table not found or has no columns.")
                return
            
            # Print table header
            print(f"\n{'Column Name':<20} | {'Data Type':<20} | {'Nullable':<8} | {'Default'}")
            print("-" * 60)
            
            # Print each column's details
            for col in columns:
                col_name = col[0]
                data_type = col[1]
                is_nullable = col[2]
                default_val = col[3] if col[3] is not None else 'NULL'
                print(f"{col_name:<20} | {data_type:<20} | {is_nullable:<8} | {default_val}")
            
            # Get row count
            count_result = connection.execute(text("SELECT COUNT(*) FROM users"))
            row_count = count_result.scalar()
            print(f"\nTotal users in database: {row_count}")
            
    except Exception as e:
        print(f"❌ Error checking users table schema: {e}")

if __name__ == "__main__":
    print("🔍 Checking users table schema...")
    check_users_schema()
