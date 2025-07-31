import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Try to import the FastAPI app
    from app.main import app
    print("✅ Successfully imported the FastAPI app!")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    
    # List all routes
    print("\nAvailable routes:")
    for route in app.routes:
        print(f"- {route.path} ({', '.join(route.methods)})")
    
except ImportError as e:
    print(f"❌ Failed to import the FastAPI app: {e}")
    print("\nPython path:", sys.path)
    
    # List the contents of the app directory
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    if os.path.exists(app_dir):
        print("\nContents of app directory:")
        for item in os.listdir(app_dir):
            print(f"- {item}")
    else:
        print(f"\nApp directory not found at: {app_dir}")
    
    print("\nCurrent working directory:", os.getcwd())
