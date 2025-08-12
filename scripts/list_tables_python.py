import psycopg2
from urllib.parse import urlparse

def list_tables():
    # Connection parameters
    db_url = "postgresql://postgres:Ayeshaayesha12%40@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    
    try:
        # Parse the database URL
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        print(f"Connecting to {hostname}:{port}/{database} as {username}...")
        
        # Connect to the database
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode="require"
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Get the PostgreSQL version
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"\n✅ Connected to PostgreSQL {version[0]}")
        
        # Get list of tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        if tables:
            print("\nTables in the database:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")
            
            # For the first table, show column information
            if tables:
                table_name = tables[0][0]
                print(f"\nColumns in '{table_name}' table:")
                cur.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                columns = cur.fetchall()
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")
        else:
            print("\nNo tables found in the database.")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error connecting to the database:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        # More specific error handling
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Authentication failed. Please check your username and password.")
        elif "connection timed out" in str(e).lower():
            print("\n⏱️ Connection timed out. Check your network and firewall settings.")
        elif "no pg_hba.conf entry" in str(e).lower():
            print("\n🔒 No pg_hba.conf entry. Your IP might not be whitelisted in Supabase.")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify your IP is whitelisted in Supabase")
        print("2. Check if the database server is running and accessible")
        print("3. Try connecting with a different client (like DBeaver or pgAdmin)")

if __name__ == "__main__":
    list_tables()
