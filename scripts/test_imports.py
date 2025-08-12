import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

print("Python Path:")
for path in sys.path:
    print(f"- {path}")

print("\nAttempting to import from app...")
try:
    from app.main import app
    print("✅ Successfully imported app.main")
except ImportError as e:
    print(f"❌ Error importing app.main: {e}")
    print(f"Current working directory: {os.getcwd()}")
    
    # List contents of the app directory
    app_dir = os.path.join(os.path.dirname(__file__), 'backend', 'app')
    if os.path.exists(app_dir):
        print("\nContents of app directory:")
        for item in os.listdir(app_dir):
            item_path = os.path.join(app_dir, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            print(f"- {item} ({item_type})")
    else:
        print(f"\nApp directory not found at: {app_dir}")
