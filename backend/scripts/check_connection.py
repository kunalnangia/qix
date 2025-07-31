import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    print("=== Database Connection Check ===")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    print(f"Loading environment from: {env_path}")
    
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return 1
        
    load_dotenv(dotenv_path=env_path, override=True)
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL not found in environment variables")
        return 1
        
    print(f"\nDatabase URL from .env:")
    print(f"  {db_url}")
    
    # Check if it's a Supabase URL
    if 'supabase' in db_url:
        print("\n✅ Detected Supabase database URL")
        if 'pooler' in db_url:
            print("✅ Using Supabase connection pooler")
        else:
            print("⚠️  Not using Supabase connection pooler")
    else:
        print("\n⚠️  This doesn't appear to be a Supabase database URL")
    
    # Check URL format
    if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
        print("\n✅ Database URL is properly formatted")
        if '+asyncpg' not in db_url:
            print("⚠️  Consider using 'postgresql+asyncpg://' for async operations")
    else:
        print("\n❌ Invalid database URL format")
        return 1
    
    print("\n=== Connection Check Complete ===")
    print("Please check the URL format and ensure it's correct for your setup.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
