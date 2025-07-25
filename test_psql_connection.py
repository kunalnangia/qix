import subprocess
import sys

def test_psql_connection():
    # Connection parameters
    host = "db.lflecyuvttemfoyixngi.supabase.co"
    port = "5432"
    database = "postgres"
    user = "postgres"
    password = "Ayeshaayesha12@"
    
    # Build the psql command
    cmd = [
        'psql',
        f'postgresql://{user}:{password}@{host}:{port}/{database}',
        '-c', '"SELECT version();"',
        '-v', 'ON_ERROR_STOP=1'
    ]
    
    # Set environment variables for psql
    env = {
        'PGPASSWORD': password,
        'PGSSLMODE': 'require'
    }
    
    print("Testing PostgreSQL connection using psql command...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    
    try:
        # Run the psql command
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check the result
        if result.returncode == 0:
            print("\n✅ Successfully connected to PostgreSQL!")
            print("Output:")
            print(result.stdout)
        else:
            print("\n❌ Connection failed:")
            print(f"Exit code: {result.returncode}")
            print("Error output:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("\n❌ psql command not found. Please make sure PostgreSQL client tools are installed.")
        print("You can install them from: https://www.postgresql.org/download/")
    except subprocess.TimeoutExpired:
        print("\n❌ Connection timed out. The server might be unreachable or not responding.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_psql_connection()
