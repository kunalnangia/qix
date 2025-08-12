import os
import asyncpg
from dotenv import load_dotenv
import asyncio
from pathlib import Path

async def test_connection():
    # Load environment variables
    env_path = str(Path(__file__).parent / '.env')
    load_dotenv(env_path)
    
    # Get database URL from environment variables
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Testing connection to: {db_url}")
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(db_url)
        
        # Test the connection
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Successfully connected to PostgreSQL: {version}")
        
        # List tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        print("\n📋 Available tables:")
        for table in tables:
            print(f"- {table['table_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
