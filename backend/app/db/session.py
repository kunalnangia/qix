import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, scoped_session
from sqlalchemy.sql import func
from contextlib import contextmanager
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from datetime import datetime
import enum
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

# Load environment variables
load_dotenv(env_path, override=True)

# Debug: Print all environment variables
print("Environment variables:")
for key, value in os.environ.items():
    if "DATABASE" in key or "SECRET" in key or "KEY" in key:
        print(f"{key} = {'*' * 8 if value else 'Not set'}")
    else:
        print(f"{key} = {value}")

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

print(f"Using DATABASE_URL: {DATABASE_URL}")

print(f"Connecting to database: {DATABASE_URL}")

# Create SQLAlchemy engine with connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    pool_timeout=30,
    connect_args={
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
@contextmanager
def get_db():
    """Generator that yields a database session and ensures it's closed after use."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

def init_db():
    """Initialize the database by creating all tables."""
    try:
        print("Initializing database...")
        create_tables()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
