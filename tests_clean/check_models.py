"""Check models for potential issues."""
import sys
import os
import inspect

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the models module
try:
    print("=== Importing models module ===")
    import backend.models as models
    print("✓ Successfully imported models module")
except Exception as e:
    print(f"✗ Error importing models module: {e}")
    raise

# List all classes in the models module
print("\n=== Listing all model classes ===")
for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj) and obj.__module__ == 'backend.models':
        print(f"- {name}")
        
        # Check for enum classes
        if hasattr(obj, '__annotations__'):
            for attr_name, attr_type in obj.__annotations__.items():
                if hasattr(attr_type, '__origin__') and attr_type.__origin__ is type:
                    print(f"  - {attr_name}: {attr_type}")
                    enum_type = attr_type.__args__[0]
                    print(f"    - Enum type: {enum_type}")
                    if hasattr(enum_type, '__members__'):
                        print(f"    - Enum members: {list(enum_type.__members__.keys())}")

print("\n=== Checking for enum definitions ===")
for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj) and issubclass(obj, str) and hasattr(obj, '__members__'):
        print(f"- {name} (enum): {list(obj.__members__.keys())}")

print("\n=== Checking for potential issues ===")
# Check for any enum classes that might be causing issues
for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj) and hasattr(obj, '__members__'):
        print(f"Checking enum class: {name}")
        try:
            # Try to get the length of the enum
            print(f"- Length: {len(obj)}")
        except Exception as e:
            print(f"- Error getting length: {e}")
        
        # Try to iterate over the enum
        try:
            print(f"- Members: {[x for x in obj]}")
        except Exception as e:
            print(f"- Error iterating: {e}")

print("\nCheck completed!")
