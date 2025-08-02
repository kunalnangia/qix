import os
import logging
import traceback
from typing import AsyncGenerator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv

# Import Base from base.py to avoid circular imports
from .base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
logger.info(f"Loading environment from: {env_path}")

# Load environment variables
load_dotenv(env_path, override=True)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

logger.info("Database URL configured")

# Base is now imported from base.py

# Create sync engine for migrations and sync operations
engine = create_engine(
    str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://"),
    echo=True,  # Enable SQL query logging for debugging
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,  # Recycle connections after 5 minutes
    pool_timeout=30,   # Wait 30 seconds before giving up on getting a connection
    connect_args={
        'keepalives': 1,  # Enable TCP keepalive
        'keepalives_idle': 30,  # Start sending keepalive packets after 30 seconds of inactivity
        'keepalives_interval': 10,  # Send keepalive packets every 10 seconds
        'keepalives_count': 5  # Consider the connection dead after 5 failed keepalive attempts
    }
)

# Create async engine for FastAPI with asyncpg
# Convert the connection string to use asyncpg
connection_string = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    connection_string,
    echo=True,  # Enable SQL query logging for debugging
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,  # Recycle connections after 5 minutes
    pool_timeout=30,   # Wait 30 seconds before giving up on getting a connection
    # For AWS Pooler, we don't need additional connect_args as they're in the connection string
    # Remove connect_args to avoid conflicts with the connection string parameters
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Scoped session for thread safety
ScopedSession = scoped_session(SessionLocal)

# Dependency for getting async database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency for FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

# Sync session for migrations and scripts
@contextmanager
def get_sync_db():
    """
    Sync database session for migrations and scripts
    """
    db = ScopedSession()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

def create_tables():
    """
    Create all database tables using sync engine
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

async def init_db():
    """
    Initialize database with async engine
    """
    import asyncio
    import time
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.sql import text
    from sqlalchemy.exc import OperationalError, InterfaceError, TimeoutError as SQLAlchemyTimeoutError
    
    async def _test_connection():
        """Test database connection with retry logic"""
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                async with async_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    logger.info("✅ Database connection test successful")
                    return True
            except (OperationalError, InterfaceError, SQLAlchemyTimeoutError) as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = retry_delay * attempt
                    logger.warning(f"⚠️ Connection attempt {attempt} failed. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                last_error = e
                break
        
        logger.error(f"❌ Failed to connect to database after {max_retries} attempts")
        if last_error:
            logger.error(f"Last error: {str(last_error)}")
            logger.debug(traceback.format_exc())
        return False
    
    async def _create_tables():
        """Create database tables with retry logic"""
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                async with async_engine.begin() as conn:
                    logger.info(f"Creating database tables (attempt {attempt}/{max_retries})...")
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("✅ Database tables created successfully")
                    return True
            except (OperationalError, InterfaceError, SQLAlchemyTimeoutError) as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = retry_delay * attempt
                    logger.warning(f"⚠️ Table creation attempt {attempt} failed. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                last_error = e
                break
        
        logger.error(f"❌ Failed to create database tables after {max_retries} attempts")
        if last_error:
            logger.error(f"Last error: {str(last_error)}")
            logger.debug(traceback.format_exc())
        return False
    
    async def _init_db():
        """Initialize the database with connection and table creation"""
        # Test connection first
        if not await _test_connection():
            return False
            
        # Create tables
        if not await _create_tables():
            return False
            
        return True
    
    # Run the async function with retry logic for the event loop
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return await _init_db()
        except RuntimeError as e:
            if "no running event loop" in str(e):
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    return await _init_db()
                except Exception as nest_error:
                    last_error = nest_error
                    logger.error(f"❌ Failed to initialize asyncio: {str(nest_error)}")
                    if attempt < max_retries:
                        wait_time = retry_delay * attempt
                        logger.warning(f"⚠️ Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    continue
            else:
                last_error = e
                logger.error(f"❌ Runtime error: {str(e)}")
                if attempt < max_retries:
                    wait_time = retry_delay * attempt
                    logger.warning(f"⚠️ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
        except Exception as e:
            last_error = e
            logger.error(f"❌ Unexpected error: {str(e)}")
            logger.debug(traceback.format_exc())
            if attempt < max_retries:
                wait_time = retry_delay * attempt
                logger.warning(f"⚠️ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            continue
    
    logger.error(f"❌ Failed to initialize database after {max_retries} attempts")
    if last_error:
        logger.error(f"Last error: {str(last_error)}")
    return False
