"""Debug import issues in the clean environment."""
import sys
import os
import importlib

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def check_import(module_name):
    """Check if a module can be imported."""
    try:
        module = importlib.import_module(module_name)
        print(f"✓ Successfully imported: {module_name}")
        print(f"   File: {getattr(module, '__file__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing {module_name}: {e}")
        return False

print("=== Python Path ===")
for path in sys.path:
    print(f"- {path}")

print("\n=== Checking Imports ===")

# Check basic imports
check_import("fastapi")
check_import("sqlalchemy")
check_import("pydantic")

# Check project imports
check_import("backend")
check_import("backend.database_sqlite")
check_import("backend.server")

# Try to import server.py directly
server_path = os.path.join(project_root, 'backend', 'server.py')
if os.path.exists(server_path):
    print(f"\n=== Server.py exists at: {server_path}")
    try:
        spec = importlib.util.spec_from_file_location("backend.server", server_path)
        if spec is None:
            print("✗ Could not create spec for backend.server")
        else:
            module = importlib.util.module_from_spec(spec)
            sys.modules["backend.server"] = module
            spec.loader.exec_module(module)
            print("✓ Successfully imported backend.server directly")
    except Exception as e:
        print(f"✗ Error importing backend.server directly: {e}")
else:
    print(f"\n✗ Server.py not found at: {server_path}")

# Check for database.py
if os.path.exists(os.path.join(project_root, 'backend', 'database.py')):
    print("\n=== database.py exists in backend/")
else:
    print("\n✗ database.py not found in backend/")

# List backend directory
backend_dir = os.path.join(project_root, 'backend')
if os.path.exists(backend_dir):
    print("\n=== Backend directory contents:")
    for item in os.listdir(backend_dir):
        print(f"- {item}")
else:
    print(f"\n✗ Backend directory not found at: {backend_dir}")
