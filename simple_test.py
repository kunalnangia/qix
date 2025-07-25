import psycopg2

try:
    # Connection parameters
    conn = psycopg2.connect(
        host="db.lflecyuvttemfoyixngi.supabase.co",
        database="postgres",
        user="postgres",
        password="Ayeshaayesha12@",
        port=5432,
        sslmode="require"
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT version()")
    db_version = cur.fetchone()
    print("✅ Successfully connected to PostgreSQL!")
    print(f"PostgreSQL version: {db_version[0]}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check if the database server is running and accessible")
    print("2. Verify the username and password are correct")
    print("3. Ensure your IP is whitelisted in Supabase")
    print("4. Try connecting with a different client (like DBeaver or pgAdmin)")
