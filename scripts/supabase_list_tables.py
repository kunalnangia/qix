from supabase import create_client, Client
import os

def list_supabase_tables():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    print(f"Connecting to Supabase at {SUPABASE_URL}...")
    
    try:
        # Initialize the client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get the current user (test authentication)
        user = supabase.auth.get_user()
        print(f"✅ Authenticated as: {user.user.email if user and hasattr(user, 'user') else 'Anonymous'}")
        
        # Try to list tables using the REST API
        print("\nAttempting to list tables...")
        
        # First, try to get tables from the information_schema
        response = supabase.table('information_schema.tables') \
            .select('table_name') \
            .eq('table_schema', 'public') \
            .execute()
        
        if hasattr(response, 'data'):
            tables = [table['table_name'] for table in response.data]
            if tables:
                print("\nTables in the database:")
                for i, table in enumerate(tables, 1):
                    print(f"{i}. {table}")
                
                # Show columns for the first table
                if tables:
                    table_name = tables[0]
                    print(f"\nColumns in '{table_name}' table:")
                    try:
                        columns = supabase.table('information_schema.columns') \
                            .select('column_name, data_type') \
                            .eq('table_name', table_name) \
                            .execute()
                        
                        if hasattr(columns, 'data'):
                            for col in columns.data:
                                print(f"  - {col['column_name']}: {col['data_type']}")
                    except Exception as e:
                        print(f"  Could not retrieve columns: {str(e)}")
            else:
                print("No tables found in the database.")
        else:
            print("\n❌ Could not retrieve table information.")
            print("Response:", response)
            
    except Exception as e:
        print(f"\n❌ Error:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        # More detailed error information
        if hasattr(e, 'args') and e.args:
            print("\nError details:")
            for i, arg in enumerate(e.args, 1):
                print(f"  {i}. {arg}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    list_supabase_tables()
