#!/usr/bin/env python3
"""
Setup script for IntelliTest AI Platform
Run this script to set up the development environment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed:")
        logger.error(f"Command: {command}")
        logger.error(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_postgresql():
    """Check if PostgreSQL is running"""
    result = run_command("pg_isready", "Checking PostgreSQL connection")
    if result is None:
        logger.warning("⚠️  PostgreSQL might not be running. Please ensure PostgreSQL is installed and running.")
        logger.info("   Installation guides:")
        logger.info("   - Windows: https://www.postgresql.org/download/windows/")
        logger.info("   - macOS: brew install postgresql")
        logger.info("   - Ubuntu: sudo apt-get install postgresql postgresql-contrib")
    else:
        logger.info("✅ PostgreSQL is running")

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not os.path.exists(".venv"):
        run_command("python -m venv .venv", "Creating virtual environment")
    else:
        logger.info("✅ Virtual environment already exists")

def install_dependencies():
    """Install Python dependencies"""
    # Determine the activate script path based on OS
    if os.name == 'nt':  # Windows
        pip_command = ".venv\\Scripts\\pip"
    else:  # Unix-like systems
        pip_command = ".venv/bin/pip"
    
    # Install dependencies
    run_command(f"{pip_command} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            run_command("copy .env.example .env", "Creating .env file from template")
            logger.info("📝 Please edit .env file with your configuration")
        else:
            logger.warning("⚠️  .env.example not found, please create .env file manually")
    else:
        logger.info("✅ .env file already exists")

def setup_database():
    """Set up database"""
    logger.info("Setting up database...")
    
    # Initialize Alembic if not already done
    if not os.path.exists("alembic"):
        run_command("alembic init alembic", "Initializing Alembic")
    
    # Create initial migration
    run_command("alembic revision --autogenerate -m 'Initial migration'", "Creating initial migration")
    
    # Apply migrations
    run_command("alembic upgrade head", "Applying database migrations")

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs", "alembic/versions"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    logger.info("🚀 Setting up IntelliTest AI Platform...")
    
    # Check requirements
    check_python_version()
    check_postgresql()
    
    # Setup environment
    setup_virtual_environment()
    install_dependencies()
    create_env_file()
    create_directories()
    
    # Database setup
    setup_database()
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("Next steps:")
    logger.info("1. Edit .env file with your configuration")
    logger.info("2. Ensure PostgreSQL is running")
    logger.info("3. Run: python main.py")
    logger.info("4. Visit: http://localhost:8001/docs")

if __name__ == "__main__":
    main()