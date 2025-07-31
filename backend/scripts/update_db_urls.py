import os
import re
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging with file output
log_file = Path(__file__).parent.parent / 'logs' / 'update_db_urls.log'
log_file.parent.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('update_db_urls')

logger.info("=== Starting Database URL Update Script ===")

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        logger.error(f"Error: .env file not found at {env_path}")
        return False
    
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded environment from: {env_path}")
    return True

def get_supabase_db_url():
    """Get the Supabase database URL from environment variables"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL not found in environment variables")
        return None
    
    # Ensure the URL is in the correct format for SQLAlchemy
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    
    logger.info(f"Using database URL: {db_url}")
    return db_url

    """Update database URL in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file contains database connection code
        db_patterns = [
            r'postgres(ql)?[+\w]*://',  # postgres://, postgresql://, postgresql+asyncpg://, etc.
            r'create_engine\s*\(',
            r'DATABASE_URL',
            r'get_db',
            r'SessionLocal',
            r'sqlalchemy'
        ]
        
        if not any(re.search(pattern, content) for pattern in db_patterns):
            return False  # Skip files that don't seem to contain DB code
        
        # Define patterns to search and replace
        replacements = [
            # Replace hardcoded database URLs
            (r'postgres(ql)?[+\\w]*://[^\\s\\'\"]+', f"'{db_url}'"),
            # Replace DATABASE_URL in os.environ.get() calls
            (r'os\\.environ\\.get\\([\"\']DATABASE_URL[\"\']\\)', f"'{db_url}'"),
            # Replace in SQLALCHEMY_DATABASE_URL
            (r'SQLALCHEMY_DATABASE_URL\\s*=\\s*[\"\'][^\"\']+[\"\']', f'SQLALCHEMY_DATABASE_URL = "{db_url}"')
        ]
        
        modified = False
        for pattern, replacement in replacements:
            new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
            if count > 0:
                modified = True
                content = new_content
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Updated: {file_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
    
    return False
def update_file(file_path, db_url):
    """Update database URL in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file contains database connection code
        db_patterns = [
            r'postgres(ql)?[+\w]*://',  # postgres://, postgresql://, postgresql+asyncpg://, etc.
            r'create_engine\s*\(',
            r'DATABASE_URL',
            r'get_db',
            r'SessionLocal',
            r'sqlalchemy'
        ]
        
        if not any(re.search(pattern, content) for pattern in db_patterns):
            return False  # Skip files that don't seem to contain DB code
        
        # Define patterns to search and replace
        replacements = [
            # Replace hardcoded database URLs
            (r'postgres(ql)?[+\\w]*://[^\\s\\\'\"]+', f"'{db_url}'"),
            # Replace DATABASE_URL in os.environ.get() calls
            (r'os\\.environ\\.get\\([\"\\']DATABASE_URL[\"\\']\\)', f"'{db_url}'"),
            # Replace in SQLALCHEMY_DATABASE_URL
            (r'SQLALCHEMY_DATABASE_URL\\s*=\\s*[\"\\'][^\"\\']+[\"\\']', f'SQLALCHEMY_DATABASE_URL = "{db_url}"')
        ]
        
        modified = False
        for pattern, replacement in replacements:
            try:
                new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
                if count > 0:
                    modified = True
                    logger.info(f" - Replaced {count} occurrence(s) of pattern: {pattern}")
                    content = new_content
            except re.error as e:
                logger.warning(f"Regex error with pattern '{pattern}': {str(e)}")
        
        if modified:
            # Create backup of original file
            backup_path = f"{file_path}.bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated content to original file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Updated: {file_path}")
            return True
        else:
            logger.debug(f"ℹ️  No changes needed for: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error processing {file_path}: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def main():
    try:
        # Load environment variables
        logger.info("Loading environment variables...")
        if not load_environment():
            logger.error("Failed to load environment variables")
            return 1
        
        # Get the database URL
        logger.info("Retrieving database URL...")
        db_url = get_supabase_db_url()
        if not db_url:
            logger.error("No valid database URL found")
            return 1
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        logger.info(f"Project root: {project_root}")
        
        # Find all Python files in the project
        logger.info("Searching for Python files...")
        python_files = list(project_root.glob('**/*.py'))
        logger.info(f"Found {len(python_files)} Python files to check")
        
        # Skip virtual environment and git directories
        skip_dirs = {'venv', '.venv', '.git', '__pycache__', 'migrations'}
        
        # Update database URLs in files
        updated_count = 0
        processed_count = 0
        
        for file_path in python_files:
            # Skip files in virtual environment and git directories
            if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
                continue
                
            processed_count += 1
            if processed_count % 50 == 0:
                logger.info(f"Processed {processed_count} files...")
            
            if update_file(file_path, db_url):
                updated_count += 1
        
        logger.info("\n=== Update Summary ===")
        logger.info(f"Total files processed: {processed_count}")
        logger.info(f"Files updated: {updated_count}")
        logger.info("Update complete!")
        return 0
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
