import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('db_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Log environment information
logger.info("=" * 80)
logger.info("STARTING DATABASE CONNECTION TEST")
logger.info("=" * 80)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Project root: {project_root}")

# Try to load environment variables
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
logger.info(f"Loading .env from: {env_path}")

if not os.path.exists(env_path):
    logger.error("❌ .env file not found!")
    sys.exit(1)

load_dotenv(env_path, override=True)
logger.info("✅ Loaded .env file")

# Log database-related environment variables
db_vars = [
    'DATABASE_URL',
    'POSTGRES_SERVER',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'POSTGRES_DB',
    'POSTGRES_PORT'
]

logger.info("\nEnvironment variables:")
for var in db_vars:
    value = os.getenv(var)
    if value and any(s in var.lower() for s in ['pass', 'secret', 'key']):
        value = f"{value[:5]}...{value[-2:] if len(value) > 7 else ''}"
    logger.info(f"  {var}: {value or 'Not set'}")

try:
    import sqlalchemy
    logger.info(f"\nSQLAlchemy version: {sqlalchemy.__version__}")
    
    # Try to create engine with direct connection string
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
        
    # Ensure proper connection string format
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    logger.info(f"\nAttempting to connect to: {db_url}")
    
    # Create engine with detailed logging
    engine = sqlalchemy.create_engine(
        db_url,
        echo=True,
        pool_pre_ping=True,
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )
    
    # Test connection
    with engine.connect() as conn:
        version = conn.execute(sqlalchemy.text("SELECT version();")).scalar()
        logger.info(f"\n✅ Successfully connected to database!")
        logger.info(f"Database version: {version}")
        
        # List all tables
        result = conn.execute(sqlalchemy.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """))
        
        tables = [row[0] for row in result.fetchall()]
        if tables:
            logger.info("\nTables in the database:")
            for table in sorted(tables):
                logger.info(f"- {table}")
        else:
            logger.warning("No tables found in the database")
    
    logger.info("\n✅ Database connection test completed successfully!")
    
except Exception as e:
    logger.error(f"\n❌ Error during database connection test:")
    logger.error(f"Type: {type(e).__name__}")
    logger.error(f"Message: {str(e)}")
    logger.error("\nStack trace:")
    logger.error(traceback.format_exc())
    sys.exit(1)

logger.info("\n" + "=" * 80)
logger.info("DATABASE CONNECTION TEST COMPLETED")
logger.info("=" * 80)
