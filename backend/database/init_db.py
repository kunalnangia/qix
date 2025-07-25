import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import database configuration
from app.db.session import Base, engine, get_db, SessionLocal, init_db

# Import all SQLAlchemy models to ensure they are registered with SQLAlchemy
from app.models.db_models import *

def init_db():
    """Initialize the database and create all tables."""
    print("Initializing database...")
    
    # Create database if it doesn't exist
    if not database_exists(engine.url):
        print(f"Creating database: {engine.url.database}")
        create_database(engine.url)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database initialization complete!")

def drop_db():
    """
    Drop all tables in the database.
    WARNING: This will delete all data in the database!
    """
    if input("WARNING: This will drop all tables in the database. Continue? (y/n): ").lower() == 'y':
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization utility")
    parser.add_argument(
        "--drop", 
        action="store_true", 
        help="Drop all tables before initializing"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        drop_db()
    
    init_db()
