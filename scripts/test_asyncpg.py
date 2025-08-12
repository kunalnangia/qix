import asyncio
import asyncpg
import ssl

async def test_connection():
    # Connection parameters
    conn_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'ssl': ssl.create_default_context()
    }
    
    print("Testing connection with asyncpg...")
    print(f"Connecting to {conn_params['host']}:{conn_params['port']}")
    print(f"Database: {conn_params['database']}")
    print(f"User: {conn_params['user']}")
    
    try:
        # Try to connect
        conn = await asyncpg.connect(**conn_params)
        
        # Test the connection
        version = await conn.fetchval('SELECT version()')
        print(f"\n✅ Successfully connected to PostgreSQL!")
        print(f"PostgreSQL version: {version}")
        
        # List all tables in the public schema
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        table_names = [row['table_name'] for row in tables]
        print(f"\nFound {len(table_names)} tables: {', '.join(table_names) if table_names else 'No tables found'}")
        
    except Exception as e:
        print(f"\n❌ Connection failed:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # More specific error handling
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Authentication failed. Please check:")
            print("1. The username and password in the connection string")
            print("2. If the password contains special characters that need to be escaped")
        elif "connection timed out" in str(e).lower():
            print("\n⏱️ Connection timed out. Please check:")
            print("1. Your internet connection")
            print("2. If the hostname and port are correct")
            print("3. If your IP is whitelisted in Supabase")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify your IP is whitelisted in Supabase")
        print("2. Try connecting with a different client (like DBeaver or pgAdmin)")
        print("3. Check Supabase dashboard for any service alerts")
    
    finally:
        if 'conn' in locals():
            await conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    asyncio.run(test_connection())
