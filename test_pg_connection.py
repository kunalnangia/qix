import psycopg2
import sys
from psycopg2 import OperationalError, Error as PgError

def test_connection():
    conn = None
    try:
        # Connection parameters
        db_params = {
            'host': 'db.lflecyuvttemfoyixngi.supabase.co',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'Ayeshaayesha@12',
            'sslmode': 'require',  # Supabase requires SSL
            'connect_timeout': 10  # Add timeout to prevent hanging
        }
        
        print("Testing connection with parameters:")
        print(f"Host: {db_params['host']}")
        print(f"Port: {db_params['port']}")
        print(f"Database: {db_params['database']}")
        print(f"User: {db_params['user']}")
        
        # Try to connect
        print("Attempting to connect to the database...")
        conn = psycopg2.connect(**db_params)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a test query
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"Database version: {db_version[0]}")
        
        # Close the cursor and connection
        cur.close()
        
    except Exception as e:
        print(f"\n❌ Error details:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        # More specific error handling
        if isinstance(e, psycopg2.OperationalError):
            print("\nThis is a connection-level error. Possible causes:")
            print("1. Incorrect hostname or port")
            print("2. The database server is not running")
            print("3. Network connectivity issues")
            print("4. Firewall blocking the connection")
            print("5. Incorrect SSL configuration")
        
        print("\nTroubleshooting steps:")
        print("1. Verify the database credentials (username/password)")
        print("2. Check if you can ping the host: ping db.lflecyuvttemfoyixngi.supabase.co")
        print("3. Try connecting with a PostgreSQL client like DBeaver or pgAdmin")
        print("4. Check Supabase dashboard for any service issues")
        print("5. Verify the database name in Supabase (it might not be 'postgres')")
        print("6. Check if your IP is whitelisted in Supabase's database settings")
    finally:
        if conn is not None:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    test_connection()
