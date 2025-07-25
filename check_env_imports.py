import sys
import os

print("=== Python Environment Check ===\n")

# Print Python version and executable
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}")

# Print Python path
print("\n=== Python Path ===")
for i, path in enumerate(sys.path, 1):
    print(f"{i}. {path}")

# Function to list directory contents
def list_dir_contents(path, indent=0, max_depth=2, current_depth=0):
    if current_depth > max_depth:
        return
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print("  " * indent + f"📁 {item}/")
                list_dir_contents(item_path, indent + 1, max_depth, current_depth + 1)
            else:
                if item.endswith(('.py', '.txt', '.md')):
                    print("  " * indent + f"📄 {item}")
    except PermissionError:
        print("  " * indent + "[Permission denied]")
    except Exception as e:
        print(f"  " * indent + f"[Error listing {path}: {str(e)}]")

# List project directory contents
print("\n=== Project Directory Structure ===")
project_root = os.path.dirname(os.path.abspath(__file__))
list_dir_contents(project_root)

# Try to find the app directory
print("\n=== Searching for app directory ===")
app_path = None
for root, dirs, files in os.walk(project_root):
    if "app" in dirs and "main.py" in os.listdir(os.path.join(root, "app")):
        app_path = os.path.join(root, "app")
        print(f"Found app directory at: {app_path}")
        print("App directory contents:")
        list_dir_contents(app_path, 1)
        break

if not app_path:
    print("Could not find app directory with main.py")
    sys.exit(1)

# Try to import from the found app directory
print("\n=== Testing Imports ===")
print(f"Adding {os.path.dirname(app_path)} to Python path")
sys.path.insert(0, os.path.dirname(app_path))

try:
    print("\nAttempting to import from app.main...")
    from app.main import app
    print("✅ Successfully imported from app.main")
except ImportError as e:
    print(f"❌ Error importing from app.main: {e}")
    print("\nFull error details:")
    import traceback
    traceback.print_exc()

print("\n=== Environment Check Complete ===")
