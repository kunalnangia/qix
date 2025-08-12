import psycopg2
from urllib.parse import urlparse

def test_connection():
    # Updated connection string with corrected password
    connection_string = "postgresql://postgres:Ayeshaayesha12@@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    
    print(f"Testing connection with updated credentials...")
    
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
        
        # Connect to the database
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode='require',
            connect_timeout=10
        )
        
        # Test the connection
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"PostgreSQL version: {version}")
            
            # List all tables to verify we can query the database
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
        
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    test_connection()
