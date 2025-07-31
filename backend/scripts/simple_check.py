print("=== Simple Environment Check ===")
print("1. Python Environment:")
import sys
print(f"   Python Version: {sys.version}")
print(f"   Executable: {sys.executable}")

print("\n2. Environment Variables:")
import os
print(f"   Current Directory: {os.getcwd()}")

# Try to load .env file
print("\n3. Loading .env file:")
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    print(f"   Looking for .env at: {os.path.abspath(env_path)}")
    
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        print("   ✅ .env file loaded successfully")
        
        # Show database URL (masking password)
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            # Mask the password in the URL for security
            import re
            masked_url = re.sub(r':[^@]+@', ':***@', db_url)
            print(f"   DATABASE_URL: {masked_url}")
        else:
            print("   ❌ DATABASE_URL not found in .env")
    else:
        print(f"   ❌ .env file not found at {os.path.abspath(env_path)}")
        
except Exception as e:
    print(f"   ❌ Error loading .env: {str(e)}")

print("\n4. Testing Database Connection:")
try:
    import sqlalchemy
    print(f"   SQLAlchemy version: {sqlalchemy.__version__}")
    
    if 'db_url' in locals() and db_url:
        try:
            # Create engine with increased timeout
            engine = sqlalchemy.create_engine(
                db_url.replace('postgres://', 'postgresql+psycopg2://', 1),
                connect_args={
                    'connect_timeout': 5,
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5
                }
            )
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text("SELECT version()"))
                db_version = result.scalar()
                print(f"   ✅ Connected to database successfully")
                print(f"   Database Version: {db_version}")
                
                # List tables
                result = conn.execute(sqlalchemy.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    LIMIT 5
                "))
                tables = [row[0] for row in result]
                print(f"   Tables in public schema: {', '.join(tables)}")
                
        except Exception as e:
            print(f"   ❌ Database connection failed: {str(e)}")
    else:
        print("   ❌ No database URL available to test connection")
        
except ImportError:
    print("   ❌ SQLAlchemy is not installed")
    print("   Please install it with: pip install sqlalchemy psycopg2-binary")

except Exception as e:
    print(f"   ❌ Error during database test: {str(e)}")

print("\n=== Test Complete ===")
