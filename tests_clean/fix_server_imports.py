"""Fix import issues in server.py by ensuring absolute imports."""
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def fix_imports():
    """Fix import statements in server.py to use absolute imports."""
    server_path = os.path.join(project_root, 'backend', 'server.py')
    
    # Read the current content
    with open(server_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the last import statement
    last_import = 0
    for i, line in enumerate(lines):
        if line.startswith(('import ', 'from ')):
            last_import = i
    
    # Add our imports after the last import
    new_imports = [
        '\n',
        '# Database imports\n',
        'from backend.database_sqlite import SessionLocal, engine, Base, get_db, init_db\n',
        'from backend import models\n',
        '\n'
    ]
    
    # Insert the new imports
    updated_lines = lines[:last_import + 1] + new_imports + lines[last_import + 1:]
    
    # Write the updated content back to the file
    with open(server_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("✓ Updated imports in server.py to use absolute imports")

if __name__ == "__main__":
    fix_imports()
