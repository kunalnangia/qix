import psycopg2
from urllib.parse import urlparse

def test_connection(db_url):
    print(f"🔍 Testing connection to: {db_url.split('@')[-1]}")
    
    try:
        # Parse the database URL
        result = urlparse(db_url)
        username = result.username
        password = result.password
        hostname = result.hostname
        port = result.port
        database = result.path.strip('/')
        
        # Create connection parameters
        conn_params = {
            'dbname': database,
            'user': username,
            'password': password,
            'host': hostname,
            'port': port,
            'connect_timeout': 5  # 5 seconds timeout
        }
        
        # Attempt to connect
        print("🔌 Attempting to connect to the database...")
        conn = psycopg2.connect(**conn_params)
        
        # If connection is successful, get server version and database name
        cur = conn.cursor()
        cur.execute("SELECT version(), current_database()")
        db_version, db_name = cur.fetchone()
        
        print("✅ Successfully connected to the database!")
        print(f"   Database: {db_name}")
        print(f"   Version: {db_version.split('on')[0].strip()}")
        
        # List all tables in the database
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"\n📋 Available tables ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}")
        return False

if __name__ == "__main__":
    db_url = "postgresql://postgres:Ayeshaayesha121@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    test_connection(db_url)
