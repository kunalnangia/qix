import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def test_connection():
    try:
        # Parse the connection string
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        # Basic connection test
        print("🔍 Attempting to connect to database...")
        conn = await asyncpg.connect(DATABASE_URL)
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Successfully connected to: {version}")
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
