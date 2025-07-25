"""Analyze server.py for missing imports and dependencies."""
import sys
import os
import ast

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def analyze_file(filepath):
    """Analyze a Python file for imports and potential issues."""
    print(f"\n=== Analyzing {os.path.basename(filepath)} ===")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the file into an AST
    tree = ast.parse(content, filename=filepath)
    
    # Collect all imports
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for name in node.names:
                imports.add(f"{module}.{name.name}" if module else name.name)
    
    print("\nImports found:")
    for imp in sorted(imports):
        print(f"- {imp}")
    
    # Check for potential missing imports
    print("\nPotential issues:")
    if 'models' not in ' '.join(imports):
        print("- 'models' module not imported but used in the code")
    if 'database' not in ' '.join(imports):
        print("- 'database' module not imported but required by the application")
    if 'database_sqlite' not in ' '.join(imports):
        print("- 'database_sqlite' module not imported but required for SQLite database")

if __name__ == "__main__":
    server_path = os.path.join(project_root, 'backend', 'server.py')
    analyze_file(server_path)
