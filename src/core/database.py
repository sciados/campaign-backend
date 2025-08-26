# src/core/database.py - FIXED VERSION - No Circular Imports

import os
import logging
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Convert postgres:// to postgresql:// if needed (Railway compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create proper async URL with asyncpg driver
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Ensure we're not mixing drivers
if "psycopg2" in ASYNC_DATABASE_URL:
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("psycopg2", "asyncpg")

logger.info(f"Sync Database URL: {DATABASE_URL[:50]}...")
logger.info(f"Async Database URL: {ASYNC_DATABASE_URL[:50]}...")

# Create both sync and async engines
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    connect_args={
        "options": "-c timezone=UTC"
    } if "postgresql" in DATABASE_URL else {}
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    connect_args={
        "server_settings": {
            "application_name": "CampaignForge_Backend",
            "timezone": "UTC"
        },
        "command_timeout": 60,
    }
)

# Base class with conflict resolution
metadata = MetaData()

class Base:
    """Base class with conflict resolution"""
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Handle table conflicts during class creation"""
        super().__init_subclass__(**kwargs)
        
        if hasattr(cls, '__table_args__'):
            if isinstance(cls.__table_args__, dict):
                if 'extend_existing' not in cls.__table_args__:
                    cls.__table_args__['extend_existing'] = True
            elif isinstance(cls.__table_args__, tuple):
                args = list(cls.__table_args__)
                table_kwargs = {}
                
                for item in args:
                    if isinstance(item, dict):
                        table_kwargs.update(item)
                        args.remove(item)
                        break
                
                table_kwargs['extend_existing'] = True
                cls.__table_args__ = tuple(args) + (table_kwargs,)
        else:
            cls.__table_args__ = {'extend_existing': True}

Base = declarative_base(
    metadata=metadata,
    cls=Base
)

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Database dependency functions
def get_db():
    """Synchronous database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db():
    """Asynchronous database dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

# Alternative sync database function for non-dependency usage
def get_sync_db_session():
    """Get a synchronous database session (not for FastAPI dependency)"""
    return SessionLocal()

# Alternative async database function for non-dependency usage  
async def get_async_db_session():
    """Get an asynchronous database session (not for FastAPI dependency)"""
    return AsyncSessionLocal()

# Alias for backward compatibility
get_async_session = get_async_db

# Table creation functions
def create_tables_sync():
    """Create tables using synchronous engine with conflict resolution"""
    try:
        logger.info("Creating database tables (synchronous)...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
        
    except Exception as e:
        if "already defined" in str(e) or "already exists" in str(e):
            logger.warning("Table conflicts detected, attempting resolution...")
            
            try:
                logger.info("Clearing metadata and recreating tables...")
                Base.metadata.clear()
                Base.metadata.create_all(bind=engine)
                logger.info("Tables recreated successfully after clearing metadata")
                return True
                
            except Exception as retry_error:
                logger.warning(f"Metadata clearing failed: {retry_error}")
                
                try:
                    logger.warning("Attempting full table recreation (data will be lost)")
                    Base.metadata.drop_all(bind=engine)
                    Base.metadata.create_all(bind=engine)
                    logger.info("Tables recreated successfully after drop/create")
                    return True
                    
                except Exception as final_error:
                    logger.error(f"All table creation methods failed: {final_error}")
                    return False
        else:
            logger.error(f"Database table creation failed: {e}")
            return False

async def create_tables_async():
    """Create tables using asynchronous engine"""
    try:
        logger.info("Creating database tables (asynchronous with asyncpg)...")
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully (async)")
        return True
        
    except Exception as e:
        logger.error(f"Async table creation failed: {e}")
        return False

# Database utility functions
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Sync database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Sync database connection test failed: {e}")
        return False

async def test_async_connection():
    """Test async database connection"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Async database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Async database connection test failed: {e}")
        return False

def get_table_info():
    """Get information about existing tables"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Found {len(tables)} existing tables: {tables}")
        return tables
    except Exception as e:
        logger.error(f"Failed to get table info: {e}")
        return []

# Database initialization function
def initialize_database():
    """Initialize database with comprehensive error handling"""
    try:
        logger.info("Initializing database...")
        
        if not test_connection():
            logger.error("Sync database connection failed")
            return False
        
        try:
            import asyncio
            try:
                asyncio.get_event_loop().run_until_complete(test_async_connection())
            except RuntimeError:
                logger.info("Skipping async connection test (event loop running)")
        except Exception as async_test_error:
            logger.warning(f"Async connection test failed: {async_test_error}")
        
        existing_tables = get_table_info()
        logger.info(f"Existing tables: {len(existing_tables)}")
        
        if create_tables_sync():
            logger.info("Database initialization completed successfully")
            return True
        else:
            logger.error("Database initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

# Cleanup functions
def cleanup_database():
    """Cleanup database connections"""
    try:
        engine.dispose()
        logger.info("Sync database connections cleaned up")
    except Exception as e:
        logger.error(f"Sync database cleanup error: {e}")

async def cleanup_async_database():
    """Cleanup async database connections"""
    try:
        await async_engine.dispose()
        logger.info("Async database connections cleaned up")
    except Exception as e:
        logger.error(f"Async database cleanup error: {e}")

# Driver verification function
def verify_database_drivers():
    """Verify that proper database drivers are being used"""
    try:
        sync_driver = engine.dialect.driver
        logger.info(f"Sync driver: {sync_driver}")
        
        async_driver = async_engine.dialect.driver
        logger.info(f"Async driver: {async_driver}")
        
        if sync_driver == "psycopg2" and async_driver == "asyncpg":
            logger.info("Database drivers correctly configured")
            return True
        else:
            logger.warning(f"Driver mismatch - Sync: {sync_driver}, Async: {async_driver}")
            return False
            
    except Exception as e:
        logger.error(f"Driver verification failed: {e}")
        return False

# Exports
__all__ = [
    'engine',
    'async_engine', 
    'Base',
    'metadata',
    'SessionLocal',
    'AsyncSessionLocal',
    'get_db',
    'get_async_db',
    'get_async_session',
    'create_tables_sync',
    'create_tables_async',
    'test_connection',
    'test_async_connection',
    'initialize_database',
    'cleanup_database',
    'cleanup_async_database',
    'get_table_info',
    'verify_database_drivers'
]