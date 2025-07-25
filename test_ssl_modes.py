import psycopg2
import ssl

def test_connection(sslmode='require'):
    print(f"\n{'='*50}")
    print(f"Testing with sslmode='{sslmode}'")
    print(f"{'='*50}")
    
    conn = None
    try:
        # Connection parameters
        conn_params = {
            'host': 'db.lflecyuvttemfoyixngi.supabase.co',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'Ayeshaayesha@12',
            'sslmode': sslmode,
            'connect_timeout': 5
        }
        
        print("Attempting to connect...")
        conn = psycopg2.connect(**conn_params)
        print("✅ Connection successful!")
        
        # Test a simple query
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"PostgreSQL version: {version}")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        
        # More detailed error information
        if isinstance(e, psycopg2.OperationalError):
            print("\nPossible solutions:")
            print("1. Check if the database server is running and accessible")
            print("2. Verify the hostname and port are correct")
            print("3. Check if your IP is whitelisted in Supabase")
            print("4. Try a different SSL mode")
            print("5. Check Supabase dashboard for any service issues")
    
    finally:
        if conn is not None:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    # Test different SSL modes
    for sslmode in ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']:
        test_connection(sslmode)
