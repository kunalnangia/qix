"""Check and fix all imports in server.py to ensure they're correct."""
import os
import sys
import re

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def check_server_imports():
    """Check and fix imports in server.py."""
    server_path = os.path.join(project_root, 'backend', 'server.py')
    
    # Read the current content
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for problematic imports
    problematic_imports = [
        (r'from\s+database\s+import', 'from backend.database_sqlite import'),
        (r'import\s+database', 'import backend.database_sqlite as database'),
        (r'from\s+models\s+import', 'from backend.models import'),
        (r'import\s+models', 'import backend.models as models'),
    ]
    
    # Track if we made any changes
    updated_content = content
    changes_made = False
    
    print("\n=== Checking for problematic imports in server.py ===")
    
    for pattern, replacement in problematic_imports:
        if re.search(pattern, updated_content):
            print(f"- Found: {pattern}")
            print(f"  Replacing with: {replacement}")
            updated_content = re.sub(pattern, replacement, updated_content)
            changes_made = True
    
    # If we made changes, write them back to the file
    if changes_made:
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("\n✓ Updated imports in server.py")
    else:
        print("\n✓ No problematic imports found in server.py")
    
    # Also check for any direct references to 'models' that might need updating
    if re.search(r'\bmodels\.', content) and 'import backend.models' not in content:
        print("\n⚠️  Found direct references to 'models' but no import. Adding import...")
        with open(server_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the first non-import line
        first_non_import = 0
        for i, line in enumerate(lines):
            if not line.startswith(('import ', 'from ')) and line.strip() != '':
                first_non_import = i
                break
        
        # Add the models import
        lines.insert(first_non_import, 'import backend.models as models\n')
        
        with open(server_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✓ Added import for backend.models")

if __name__ == "__main__":
    check_server_imports()
