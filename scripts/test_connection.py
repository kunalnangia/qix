import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Database URL - using the one from your .env file
DATABASE_URL = "postgresql://postgres:Ayeshaayesha@12@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"

try:
    # Create engine and test connection
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Test basic connection
        print("Testing database connection...")
        result = conn.execute(text("SELECT version()"))
        print(f"✅ Connected to: {result.scalar()}")
        
        # Test if we can query the database
        print("\nTesting query execution...")
        result = conn.execute(text("SELECT current_database()"))
        print(f"✅ Current database: {result.scalar()}")
        
        # List all tables (should be empty for now)
        print("\nListing tables...")
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        print(f"Found {len(tables)} tables: {', '.join(tables) if tables else 'No tables found'}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check if the database server is running and accessible")
    print("2. Verify the database URL is correct")
    print("3. Check your internet connection")
    print("4. Ensure the database exists and the user has proper permissions")
    print("5. Try connecting with psql: psql postgresql://postgres:Ayeshaayesha@12@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres")
