import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid
import bcrypt

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Load environment variables
load_dotenv()

def test_database_connection(engine):
    """Test database connection and return connection status"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            logger.info(f"Database connection successful. Version: {db_version}")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def create_test_user():
    """Create a test user directly in the database"""
    try:
        # Get database URL from environment variables
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL not found in environment variables")
            return False
            
        logger.info(f"Using database URL: {db_url}")
        
        # Create database engine with connection pool settings
        engine = create_engine(
            db_url,
            echo=True,  # Enable SQL echo for debugging
            pool_pre_ping=True,  # Test connections before using them
            pool_recycle=300,  # Recycle connections after 5 minutes
            connect_args={"connect_timeout": 10}  # 10 second connection timeout
        )
        
        # Test the database connection
        if not test_database_connection(engine):
            logger.error("Failed to connect to the database. Please check your connection settings.")
            return False
            
        # Create a new session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if user already exists
        try:
            # First, check if the users table exists
            table_check = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """)
            table_exists = session.execute(table_check).scalar()
            
            if not table_exists:
                logger.info("Users table does not exist. Creating it now...")
                self.create_users_table(session)
                table_exists = session.execute(table_check).scalar()
                if not table_exists:
                    logger.error("Failed to create users table")
                    return False
            
            # Now check if the user exists
            query = text("""
                SELECT id, email, is_active, created_at, role 
                FROM users 
                WHERE email = :email
            """)
            result = session.execute(query, {"email": "test@example.com"})
            existing_user = result.fetchone()
            
            if existing_user:
                logger.info(f"User already exists - ID: {existing_user[0]}, Email: {existing_user[1]}")
                logger.info(f"Account status: {'Active' if existing_user[2] else 'Inactive'}, Created: {existing_user[3]}")
                logger.info("You can now log in with email: test@example.com / Password: test1234")
                return True
                
        except Exception as e:
            logger.error(f"Error checking for existing user: {str(e)}")
            logger.info("Attempting to create the users table if it doesn't exist...")
    def create_users_table(self, session):
        """Create the users table if it doesn't exist"""
        try:
            create_table_sql = """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'users') THEN
                    CREATE TABLE users (
                        id VARCHAR(255) PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        full_name VARCHAR(255),
                        hashed_password VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'user',
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Create an index on the email column for faster lookups
                    CREATE INDEX idx_users_email ON users (email);
                    
                    -- Add a trigger to update the updated_at column on row update
                    CREATE OR REPLACE FUNCTION update_modified_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                    
                    CREATE TRIGGER update_users_updated_at
                    BEFORE UPDATE ON users
                    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
                    
                    RAISE NOTICE 'Created users table';
                END IF;
            END $$;
            """
            session.execute(text(create_table_sql))
            session.commit()
            logger.info("Successfully created users table with indexes and triggers")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating users table: {str(e)}")
            return False
            
        try:
            # Generate a strong password
            password = "Test@1234!"  # More secure password
            
            # Hash the password with a new salt
            salt = bcrypt.gensalt(rounds=12)  # Increased work factor for better security
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # Get current UTC time
            now = datetime.now(timezone.utc)
            
            # Create user with additional fields for better security
            user_data = {
                "id": str(uuid.uuid4()),
                "email": "test@example.com",
                "full_name": "Test Administrator",
                "hashed_password": hashed_password,
                "is_active": True,
                "role": "admin",
                "created_at": now,
                "updated_at": now
            }
        
            # Insert user
            query = text("""
                INSERT INTO users (id, email, full_name, hashed_password, is_active, role, created_at, updated_at)
                VALUES (:id, :email, :full_name, :hashed_password, :is_active, :role, :created_at, :updated_at)
                RETURNING id, email, created_at
            """)
            
            result = session.execute(query, user_data)
            created_user = result.fetchone()
            session.commit()
            
            if created_user:
                logger.info(f"✅ Successfully created test user - ID: {created_user[0]}, Email: {created_user[1]}")
                logger.info(f"Account created at: {created_user[2]}")
                logger.info("You can now log in with email: test@example.com / Password: test1234")
                return True
            else:
                logger.error("Failed to create user - no data returned from insert")
                return False
                
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            if 'session' in locals():
                session.rollback()
            return False
        finally:
            if 'session' in locals():
                session.close()
                logger.info("Database connection closed")

if __name__ == "__main__":
    import uuid  # Import here to avoid circular imports
    create_test_user()
