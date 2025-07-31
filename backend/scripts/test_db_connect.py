import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    print("=== Database Connection Test ===\n")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    print(f"1. Loading environment from: {env_path}")
    
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        return 1
        
    load_dotenv(dotenv_path=env_path, override=True)
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return 1
    
    print(f"\n2. Database URL from .env:")
    print(f"   {db_url}")
    
    # Ensure URL uses asyncpg
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+asyncpg://', 1)
        print("\n   Converted to asyncpg format:")
        print(f"   {db_url}")
    
    # Create SQLAlchemy engine
    try:
        print("\n3. Creating SQLAlchemy engine...")
        engine = create_engine(db_url)
        
        # Test connection
        print("4. Testing database connection...")
        with engine.connect() as conn:
            print("   ✅ Successfully connected to database")
            
            # Get database version
            result = conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            print(f"\n5. Database version:")
            print(f"   {db_version}")
            
            # List all tables in public schema
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            print(f"\n6. Tables in public schema (first 10):")
            for table in tables[:10]:
                print(f"   - {table}")
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more tables")
            
        return 0
        
    except Exception as e:
        print(f"\n❌ Error connecting to database:")
        print(f"   {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
