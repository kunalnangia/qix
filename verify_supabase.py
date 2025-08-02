import psycopg2
from urllib.parse import urlparse
import sys

def test_connection(connection_string):
    print(f"🔍 Testing connection to: {connection_string}")
    
    try:
        # Parse the connection string
        result = urlparse(connection_string)
        
        # Extract connection parameters
        dbname = result.path[1:]  # Remove the leading '/'
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432  # Default PostgreSQL port
        
        print(f"• Host: {host}")
        print(f"• Port: {port}")
        print(f"• Database: {dbname}")
        print(f"• User: {user}")
        
        # Try to connect
        print("\n🔌 Attempting to connect to the database...")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=10
        )
        
        # If we get here, connection was successful
        print("✅ Successfully connected to the database!")
        
        # Get database version
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"\n📊 Database version: {version}")
            
            # Get list of tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            print(f"\n📋 Found {len(tables)} tables in the database:")
            for table in tables:
                print(f"  • {table}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        
        # Provide specific troubleshooting tips based on error
        if "Connection refused" in str(e):
            print("\n🔧 Troubleshooting:")
            print("1. Check if the database server is running")
            print("2. Verify the hostname and port are correct")
            print("3. Check if your IP is whitelisted in the database firewall")
            
        elif "authentication failed" in str(e).lower():
            print("\n🔧 Troubleshooting:")
            print("1. Verify the username and password are correct")
            print("2. Check if the user has permission to access the database")
            
        elif "does not exist" in str(e).lower():
            print("\n🔧 Troubleshooting:")
            print("1. Verify the database name is correct")
            print("2. The database may need to be created")
            
        return False

if __name__ == "__main__":
    # Test with the provided connection string
    connection_string = "postgresql://postgres:Ayeshaayesha121@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    success = test_connection(connection_string)
    
    if not success:
        print("\n❌ Database connection test failed. Please check the error message above.")
        sys.exit(1)
    else:
        print("\n✅ Database connection test completed successfully!")
