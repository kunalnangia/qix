"""Debug Python path and module imports."""
import sys
import os

print("\n=== Python Path ===")
for path in sys.path:
    print(f"- {path}")

print("\n=== Current Working Directory ===")
print(f"- {os.getcwd()}")

print("\n=== Testing Imports ===")
try:
    import backend.database_sqlite
    print("✓ Successfully imported backend.database_sqlite")
except ImportError as e:
    print(f"✗ Failed to import backend.database_sqlite: {e}")

try:
    from backend.server import app
    print("✓ Successfully imported backend.server.app")
except ImportError as e:
    print(f"✗ Failed to import backend.server.app: {e}")

print("\n=== Module Search Path ===")
for path in sys.path:
    backend_path = os.path.join(path, 'backend')
    if os.path.exists(backend_path):
        print(f"Found backend at: {backend_path}")
        print("Contents:", os.listdir(backend_path))
