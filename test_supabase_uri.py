import psycopg2
from urllib.parse import urlparse

def test_connection():
    # Connection string from Supabase dashboard
    connection_string = "postgresql://postgres:Ayeshaayesha12@@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    
    print(f"Testing connection with Supabase URI...")
    
    try:
        # Parse the connection string
        result = urlparse(connection_string)
        
        # Extract connection parameters
        db_params = {
            'host': result.hostname,
            'port': result.port,
            'database': result.path[1:],  # Remove leading '/'
            'user': result.username,
            'password': result.password,
            'sslmode': 'require'  # Force SSL for Supabase
        }
        
        print("Connection parameters:")
        for key, value in db_params.items():
            if key == 'password':
                print(f"  {key}: {'*' * len(value) if value else 'None'}")
            else:
                print(f"  {key}: {value}")
        
        # Try to connect
        print("\nAttempting to connect...")
        conn = psycopg2.connect(**db_params)
        
        # Test the connection
        with conn.cursor() as cur:
            # Get PostgreSQL version
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"\n✅ Successfully connected to PostgreSQL!")
            print(f"PostgreSQL version: {version}")
            
            # List all tables in the public schema
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            print(f"\nFound {len(tables)} tables: {', '.join(tables) if tables else 'No tables found'}")
        
    except Exception as e:
        print(f"\n❌ Connection failed:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # More specific error handling
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Authentication failed. Please check:")
            print("1. The username and password in the connection string")
            print("2. If the password contains special characters that need to be URL-encoded")
        elif "connection timed out" in str(e).lower():
            print("\n⏱️ Connection timed out. Please check:")
            print("1. Your internet connection")
            print("2. If the hostname and port are correct")
            print("3. If your IP is whitelisted in Supabase")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Try copying the connection string directly from Supabase dashboard")
        print("2. Check if you can ping the host: ping db.lflecyuvttemfoyixngi.supabase.co")
        print("3. Try connecting using a different client (like DBeaver or pgAdmin)")
        print("4. Check Supabase dashboard for any service alerts")
        print("5. Verify your IP is whitelisted in Supabase's database settings")
    
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    test_connection()
