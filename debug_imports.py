import os
import sys

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Print Python path
print("\nPython path:")
for path in sys.path:
    print(f"- {path}")

# Function to list directory contents
def list_dir(path, indent=0):
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print("  " * indent + f"📁 {item}/")
                # Only go one level deep for now
                if indent == 0:
                    list_dir(item_path, indent + 1)
            else:
                print("  " * indent + f"📄 {item}")
    except PermissionError:
        print("  " * indent + "[Permission denied]")
    except Exception as e:
        print("  " * indent + f"[Error: {str(e)}]")

# List project root contents
print("\nProject root contents:")
list_dir(".")

# Try to import from backend.app
print("\nAttempting to import from backend.app...")
try:
    from backend.app.main import app
    print("✅ Successfully imported from backend.app.main")
except ImportError as e:
    print(f"❌ Error importing from backend.app.main: {e}")
    print("\nAttempting to import from app...")
    try:
        from app.main import app
        print("✅ Successfully imported from app.main")
    except ImportError as e:
        print(f"❌ Error importing from app.main: {e}")

# If we still can't import, try to find the app directory
print("\nSearching for app directory...")
app_path = None
for root, dirs, _ in os.walk("."):
    if "app" in dirs and "main.py" in os.listdir(os.path.join(root, "app")):
        app_path = os.path.join(root, "app")
        print(f"Found app directory at: {app_path}")
        break

if app_path:
    print("\nApp directory structure:")
    list_dir(app_path)
    
    # Try to import using the found path
    sys.path.insert(0, os.path.dirname(app_path))
    print(f"\nAdded {os.path.dirname(app_path)} to Python path")
    
    print("\nAttempting to import from app.main...")
    try:
        from app.main import app
        print("✅ Successfully imported from app.main")
    except ImportError as e:
        print(f"❌ Error importing from app.main: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
else:
    print("❌ Could not find app directory with main.py")
