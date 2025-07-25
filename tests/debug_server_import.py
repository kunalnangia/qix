"""Debug backend.server import."""
import sys
import os
import importlib.util

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# Try to import backend.server
print("\n=== Attempting to import backend.server ===")
try:
    # Import the module
    spec = importlib.util.spec_from_file_location(
        "backend.server",
        os.path.join(project_root, "backend", "server.py")
    )
    if spec is None:
        print("✗ Failed to create spec for backend.server")
    else:
        print(f"✓ Created spec for backend.server: {spec.origin}")
        
        # Load the module
        module = importlib.util.module_from_spec(spec)
        sys.modules["backend.server"] = module
        try:
            spec.loader.exec_module(module)
            print("✓ Successfully imported backend.server")
            
            # List the module's attributes
            print("\nModule attributes:")
            for attr in dir(module):
                if not attr.startswith('_'):
                    print(f"- {attr}")
                    
        except Exception as e:
            print(f"✗ Error loading module: {str(e)}")
            
except Exception as e:
    print(f"✗ Error importing backend.server: {str(e)}")

# Check if backend is a package
print("\n=== Checking backend package structure ===")
backend_path = os.path.join(project_root, "backend")
if os.path.exists(backend_path):
    print(f"Backend directory exists at: {backend_path}")
    print("Contents:")
    for item in os.listdir(backend_path):
        print(f"- {item}")
else:
    print(f"✗ Backend directory not found at: {backend_path}")
