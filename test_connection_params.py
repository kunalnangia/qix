import psycopg2

def test_connection_params():
    # Base connection parameters
    base_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
    }
    
    # Different connection parameter variations to try
    connection_variations = [
        {**base_params, 'sslmode': 'require'},
        {**base_params, 'sslmode': 'prefer'},
        {**base_params, 'sslmode': 'allow'},
        {**base_params, 'sslmode': 'disable'},
        {**base_params, 'sslmode': 'verify-ca'},
        {**base_params, 'sslmode': 'verify-full'},
    ]
    
    for i, params in enumerate(connection_variations, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: sslmode='{params.get('sslmode', 'not set')}'")
        print(f"{'='*50}")
        
        conn = None
        try:
            # Print connection parameters (hiding password)
            safe_params = params.copy()
            safe_params['password'] = '*' * len(safe_params['password']) if safe_params['password'] else 'None'
            print("Connection parameters:")
            for key, value in safe_params.items():
                print(f"  {key}: {value}")
            
            # Try to connect
            print("\nAttempting to connect...")
            conn = psycopg2.connect(**params)
            
            # Test the connection
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"✅ Success! PostgreSQL version: {version}")
                
                # List all tables if connection is successful
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [row[0] for row in cur.fetchall()]
                print(f"\nFound {len(tables)} tables: {', '.join(tables) if tables else 'No tables found'}")
            
            # If we get here, connection was successful
            print("\nConnection successful with these parameters!")
            return
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            
            # More specific error handling
            if "password authentication failed" in str(e).lower():
                print("🔑 Authentication failed. Please check your username and password.")
            elif "no pg_hba.conf entry" in str(e).lower():
                print("🔒 No pg_hba.conf entry. Check if your IP is whitelisted in Supabase.")
            elif "connection timed out" in str(e).lower():
                print("⏱️ Connection timed out. Check your network and firewall settings.")
            
        finally:
            if conn is not None:
                conn.close()
    
    print("\nAll connection attempts failed. Here are some troubleshooting steps:")
    print("1. Verify your IP is whitelisted in Supabase")
    print("2. Check if the database server is running and accessible")
    print("3. Verify the username and password are correct")
    print("4. Try connecting with a different client (like DBeaver or pgAdmin)")
    print("5. Check Supabase dashboard for any service alerts")

if __name__ == "__main__":
    test_connection_params()
