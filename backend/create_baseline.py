import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import platform

def get_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"error: {str(e)}"

def get_directory_structure(root_path: Path) -> Dict[str, Any]:
    """Recursively get directory structure and file hashes"""
    root_path = root_path.absolute()
    structure = {
        "name": root_path.name,
        "type": "directory",
        "path": str(root_path),
        "children": []
    }
    
    try:
        for item in root_path.iterdir():
            if item.name.startswith('.'):
                continue
                
            if item.is_dir() and item.name not in ['__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules']:
                structure["children"].append(get_directory_structure(item))
            elif item.is_file() and item.suffix not in ['.pyc', '.pyo', '.pyd']:
                structure["children"].append({
                    "name": item.name,
                    "type": "file",
                    "path": str(item),
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                    "hash": get_file_hash(item) if item.suffix in ['.py', '.json', '.env', '.md', '.txt', '.yaml', '.yml'] else "skipped"
                })
    except Exception as e:
        structure["error"] = str(e)
        
    return structure

def get_python_environment() -> Dict[str, str]:
    """Get Python environment information"""
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine()
    }

def get_pip_packages() -> List[Dict[str, str]]:
    """Get installed Python packages"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = []
        for line in result.stdout.split('\n'):
            if '==' in line:
                name, version = line.strip().split('==', 1)
                packages.append({"name": name, "version": version})
        return packages
    except Exception as e:
        return [{"error": f"Failed to get pip packages: {str(e)}"}]

def get_git_info() -> Dict[str, str]:
    """Get git repository information"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()
        
        return {
            "branch": branch,
            "commit": commit_hash,
            "has_uncommitted_changes": bool(subprocess.run(
                ["git", "diff", "--quiet"],
                capture_output=True
            ).returncode)
        }
    except Exception as e:
        return {"error": f"Failed to get git info: {str(e)}"}

def create_baseline() -> Dict[str, Any]:
    """Create a baseline of the application"""
    project_root = Path(__file__).parent.absolute()
    timestamp = datetime.utcnow().isoformat()
    
    baseline = {
        "metadata": {
            "timestamp": timestamp,
            "baseline_type": "second_baseline",
            "project_root": str(project_root)
        },
        "environment": get_python_environment(),
        "git": get_git_info(),
        "dependencies": {
            "python_packages": get_pip_packages()
        },
        "file_structure": get_directory_structure(project_root)
    }
    
    return baseline

def save_baseline(baseline: Dict[str, Any]) -> Path:
    """Save baseline to a JSON file"""
    project_root = Path(__file__).parent.absolute()
    baseline_dir = project_root / "baselines"
    baseline_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    baseline_file = baseline_dir / f"baseline_v2_{timestamp}.json"
    
    with open(baseline_file, 'w', encoding='utf-8') as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)
    
    return baseline_file

def main():
    print("🚀 Creating second baseline of the application...")
    
    try:
        # Create baseline
        baseline = create_baseline()
        
        # Save baseline to file
        baseline_file = save_baseline(baseline)
        print(f"✅ Baseline created successfully: {baseline_file}")
        
        # Print summary
        print("\n📋 Baseline Summary:")
        print(f"- Timestamp: {baseline['metadata']['timestamp']}")
        print(f"- Python Version: {baseline['environment']['python_version']}")
        print(f"- Project Root: {baseline['metadata']['project_root']}")
        
        # Count files and directories
        def count_items(node):
            if "children" not in node:
                return 1, 0
            files = 0
            dirs = 1  # Count the current directory
            for child in node["children"]:
                if child["type"] == "file":
                    files += 1
                else:
                    child_dirs, child_files = count_items(child)
                    dirs += child_dirs
                    files += child_files
            return dirs, files
        
        total_dirs, total_files = count_items(baseline["file_structure"])
        print(f"- Total Directories: {total_dirs}")
        print(f"- Total Files: {total_files}")
        print(f"- Python Packages: {len(baseline['dependencies']['python_packages'])}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating baseline: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
