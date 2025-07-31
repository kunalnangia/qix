import asyncio
import logging
import traceback
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError, InterfaceError, TimeoutError as SQLAlchemyTimeoutError
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Configure async engine with enhanced settings for asyncpg
connection_string = (
    str(DATABASE_URL)
    .replace("postgresql://", "postgresql+asyncpg://")
    + "?connect_timeout=10"
    + "&keepalives=1"
    + "&keepalives_idle=30"
    + "&keepalives_interval=10"
    + "&keepalives_count=5"
    + "&command_timeout=60"
    + "&application_name=intellitest_test"
    + "&statement_timeout=60000"
)

async_engine = create_async_engine(
    connection_string,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    pool_timeout=30,
    connect_args={
        'server_settings': {
            'application_name': 'intellitest_test',
            'statement_timeout': '60000'  # 60 seconds statement timeout
        }
    }
)

async def test_connection(max_retries=3, retry_delay=5):
    """Test database connection with retry logic"""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt}/{max_retries})...")
            async with async_engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"✅ Successfully connected to PostgreSQL version: {version}")
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
            logger.error(f"❌ Unexpected error during connection attempt {attempt}: {str(e)}")
            logger.debug(traceback.format_exc())
            if attempt < max_retries:
                wait_time = retry_delay * attempt
                await asyncio.sleep(wait_time)
            continue
    
    logger.error(f"❌ Failed to connect to database after {max_retries} attempts")
    if last_error:
        logger.error(f"Last error: {str(last_error)}")
    return False

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error running test: {str(e)}")
        logger.debug(traceback.format_exc())
    finally:
        # Close the engine when done
        if 'async_engine' in locals():
            asyncio.run(async_engine.dispose())
            logger.info("Database engine closed")
