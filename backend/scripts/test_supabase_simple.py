import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_connection():
    # Database connection parameters
    db_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'port': '5432',
        'connect_timeout': 5
    }
    
    print("Testing Supabase connection...")
    print(f"Connecting to: {db_params['host']}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("\n✅ Successfully connected to Supabase!")
        print(f"PostgreSQL version: {version[0]}")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("\nNo tables found in the database.")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase:")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SUPABASE DATABASE CONNECTION TEST")
    print("=" * 80)
    
    success = test_connection()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST COMPLETED SUCCESSFULLY")
    else:
        print("❌ TEST FAILED")
    print("=" * 80)
