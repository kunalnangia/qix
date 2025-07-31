import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

def test_supabase_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return False
    
    print(f"🔍 Testing connection to Supabase PostgreSQL...")
    print(f"   Database URL: {database_url.split('@')[-1]}")  # Hide credentials in output
    
    try:
        # Create engine with connection pooling
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Check connection before using it
            pool_recycle=300,    # Recycle connections after 5 minutes
            echo=True           # Show SQL queries
        )
        
        # Test connection with a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Successfully connected to PostgreSQL version: {version}")
            
            # Check if the database is empty
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"📊 Found {len(tables)} tables in the database")
                print(f"   Tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
            else:
                print("ℹ️  No tables found in the database. You'll need to run migrations.")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to connect to Supabase PostgreSQL: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify the Supabase database is running and accessible")
        print("3. Check if the credentials in .env are correct")
        print("4. Ensure your IP is whitelisted in Supabase dashboard")
        return False

if __name__ == "__main__":
    test_supabase_connection()
