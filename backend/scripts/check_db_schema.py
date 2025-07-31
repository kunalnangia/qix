import psycopg2
from psycopg2 import sql
from tabulate import tabulate

def check_database_schema():
    # Database connection parameters
    db_params = {
        'host': 'db.lflecyuvttemfoyixngi.supabase.co',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Ayeshaayesha12@',
        'port': '5432',
        'connect_timeout': 5
    }
    
    print("=" * 80)
    print("DATABASE SCHEMA CHECK")
    print("=" * 80)
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("\n❌ No tables found in the database!")
            return
            
        print("\n📋 Found tables:")
        for table in tables:
            print(f"- {table}")
        
        # Check if users table exists
        if 'users' not in tables:
            print("\n❌ 'users' table not found in the database!")
            return
            
        # Get columns in users table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("\n📋 'users' table columns:")
        print(tabulate(
            columns, 
            headers=['Column', 'Type', 'Nullable', 'Default'],
            tablefmt='grid'
        ))
        
        # Check for required columns
        required_columns = ['email', 'hashed_password', 'is_active']
        existing_columns = [col[0] for col in columns]
        missing_columns = [col for col in required_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"\n❌ Missing required columns: {', '.join(missing_columns)}")
        else:
            print("\n✅ All required columns are present")
        
        # Check if there are any users in the database
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"\n👥 Total users in database: {user_count}")
        
        if user_count > 0:
            print("\nSample users:")
            cursor.execute("SELECT id, email, is_active, created_at FROM users LIMIT 5;")
            users = cursor.fetchall()
            print(tabulate(
                users,
                headers=['ID', 'Email', 'Active', 'Created At'],
                tablefmt='grid'
            ))
        
        print("\n✅ Database schema check completed")
        
    except Exception as e:
        print(f"\n❌ Error checking database schema: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_schema()
