import psycopg2
import socket
import ssl
from urllib.parse import urlparse

def check_connection():
    # Connection parameters
    conn_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'sslmode': 'require',
        'connect_timeout': 5
    }
    
    print("Testing connection to Supabase PostgreSQL...")
    
    # 1. Test basic network connectivity
    print("\n1. Testing network connectivity...")
    try:
        sock = socket.create_connection((conn_params['host'], conn_params['port']), timeout=5)
        print(f"✅ Successfully connected to {conn_params['host']}:{conn_params['port']}")
        sock.close()
    except Exception as e:
        print(f"❌ Network connection failed: {e}")
        print("   Please check your internet connection and firewall settings.")
        return
    
    # 2. Test SSL connection
    print("\n2. Testing SSL handshake...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((conn_params['host'], conn_params['port'])) as sock:
            with context.wrap_socket(sock, server_hostname=conn_params['host']) as ssock:
                print(f"✅ SSL handshake successful with {ssock.version()}")
    except Exception as e:
        print(f"❌ SSL handshake failed: {e}")
    
    # 3. Test PostgreSQL connection
    print("\n3. Testing PostgreSQL connection...")
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"   PostgreSQL version: {version}")
            
            # List all tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            print(f"\n   Found {len(tables)} tables: {', '.join(tables) if tables else 'No tables found'}")
            
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("\nTroubleshooting steps:")
        if "password authentication failed" in str(e).lower():
            print("1. Verify the username and password are correct")
            print("2. Check for any special characters in the password that might need escaping")
        elif "connection timed out" in str(e).lower():
            print("1. Check if the database server is running and accessible")
            print("2. Verify the hostname and port are correct")
        print("3. Check if your IP is whitelisted in Supabase dashboard")
        print("4. Try connecting with a different client (like DBeaver or pgAdmin)")
    
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    check_connection()
