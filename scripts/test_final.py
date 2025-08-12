import psycopg2
from urllib.parse import urlparse

def test_connection():
    # Connection parameters
    db_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'sslmode': 'require'
    }
    
    print("Testing connection to PostgreSQL...")
    print(f"Host: {db_params['host']}")
    print(f"Port: {db_params['port']}")
    print(f"Database: {db_params['database']}")
    print(f"User: {db_params['user']}")
    
    conn = None
    try:
        # Try to connect
        print("\nAttempting to connect...")
        conn = psycopg2.connect(**db_params)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a test query
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"PostgreSQL version: {version}")
        
        # List all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"\nFound {len(tables)} tables: {', '.join(tables) if tables else 'No tables found'}")
        
        # Close the cursor
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Connection failed:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # More specific error handling
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Authentication failed. Please check:")
            print("1. The username and password")
            print("2. If the password needs to be URL-encoded")
        elif "connection timed out" in str(e).lower():
            print("\n⏱️ Connection timed out. Please check:")
            print("1. Your internet connection")
            print("2. If the hostname and port are correct")
            print("3. If your IP is whitelisted in Supabase")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify your IP is whitelisted in Supabase")
        print("2. Try connecting with a different client")
        print("3. Check Supabase dashboard for any service alerts")
    
    finally:
        if conn is not None:
            conn.close()
            print("\nConnection closed.")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_connection()
