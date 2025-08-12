from supabase import create_client, Client
import os

def test_supabase_connection():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    print("Testing Supabase connection using JavaScript client...")
    print(f"Supabase URL: {SUPABASE_URL}")
    
    try:
        # Initialize the client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test the connection by fetching a table
        print("\nAttempting to fetch data from 'users' table...")
        response = supabase.table('users').select("*").limit(1).execute()
        
        # Check if we got a response
        if hasattr(response, 'data'):
            print("✅ Successfully connected to Supabase!")
            print(f"Found {len(response.data)} users")
            if response.data:
                print("\nFirst user:")
                for key, value in response.data[0].items():
                    print(f"  {key}: {value}")
        else:
            print("❌ Connection failed. Response:")
            print(response)
            
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # More specific error handling
        if "401" in str(e):
            print("\n🔑 Authentication failed. Please check your Supabase API key.")
        elif "404" in str(e):
            print("\n🔍 Resource not found. The table might not exist or you might not have permissions.")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify the Supabase URL and API key are correct")
        print("2. Check if your IP is whitelisted in Supabase")
        print("3. Check Supabase dashboard for any service alerts")

if __name__ == "__main__":
    test_supabase_connection()
