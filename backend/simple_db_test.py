import os
import sys
import psycopg2
from psycopg2 import OperationalError

def test_connection():
    print("🔍 Testing database connection...")
    
    # Connection parameters from the URL
    db_params = {
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'database': 'postgres',
        'user': 'postgres.lflecyuvttemfoyixngi',
        'password': 'Ayeshaayesha121',
        'port': '5432'
    }
    
    try:
        print("Attempting to connect to the database...")
        connection = psycopg2.connect(**db_params)
        print("✅ Successfully connected to the database!")
        
        # Create a cursor to execute a query
        cursor = connection.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"📊 Database version: {db_version[0]}")
        
        # List tables in the database
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f"\nFound {len(tables)} tables in the database:")
            for table in tables[:10]:  # Show first 10 tables
                print(f"- {table[0]}")
            if len(tables) > 10:
                print(f"... and {len(tables) - 10} more tables")
        else:
            print("\nNo tables found in the database.")
        
        cursor.close()
        connection.close()
        return True
        
    except OperationalError as e:
        print(f"❌ Error connecting to the database: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify the Supabase database is running")
        print("3. Check if your IP is whitelisted in Supabase dashboard")
        print("4. Ensure the database credentials are correct")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database connection test...")
    test_connection()
    print("\nTest complete.")
