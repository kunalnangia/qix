import psycopg2
from urllib.parse import urlparse

def test_supabase_connection():
    # Supabase connection string format
    connection_string = "postgresql://postgres:Ayeshaayesha@12@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    
    print(f"Testing connection to: {connection_string}")
    
    try:
        # Parse the connection string
        result = urlparse(connection_string)
        username = result.username
        password = result.password
        database = result.path[1:]  # Remove leading '/'
        hostname = result.hostname
        port = result.port
        
        print(f"Connecting to {hostname}:{port} as user '{username}'")
        print(f"Database: {database}")
        
        # Try to connect
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode='require',
            connect_timeout=5
        )
        
        # Test the connection
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ Success! PostgreSQL version: {version}")
            
    except Exception as e:
        print(f"\n❌ Connection failed:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Specific error handling
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Authentication failed. Please check:")
            print("1. The username and password in the connection string")
            print("2. If the password contains special characters that need to be URL-encoded")
            print("3. If the user has the correct permissions in Supabase")
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
    test_supabase_connection()
