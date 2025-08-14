# src/core/database.py - FIXED VERSION for AsyncEngine with proper driver
import os
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import asyncio

logger = logging.getLogger(__name__)

# ============================================================================
# ✅ FIXED: Database Configuration with proper async driver
# ============================================================================

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Convert postgres:// to postgresql:// if needed (Railway compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 🔧 CRITICAL FIX: Create proper async URL with asyncpg driver
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# 🔧 ADDITIONAL FIX: Ensure we're not mixing drivers
if "psycopg2" in ASYNC_DATABASE_URL:
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("psycopg2", "asyncpg")

logger.info(f"🔗 Sync Database URL: {DATABASE_URL[:50]}...")
logger.info(f"🔗 Async Database URL: {ASYNC_DATABASE_URL[:50]}...")

# ============================================================================
# ✅ FIXED: Create both sync and async engines with proper drivers
# ============================================================================

# Synchronous engine for table creation and simple operations (uses psycopg2)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,  # Set to True for SQL debugging
    # Add connection args for better compatibility
    connect_args={
        "options": "-c timezone=UTC"
    } if "postgresql" in DATABASE_URL else {}
)

# 🔧 CRITICAL FIX: Asynchronous engine with asyncpg driver
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    # 🔧 FIXED: Proper asyncpg connection args
    connect_args={
        "server_settings": {
            "application_name": "CampaignForge_Backend",
            "timezone": "UTC"
        },
        # 🔧 CRITICAL: Ensure asyncpg-specific settings
        "command_timeout": 60,
    }
)

# ============================================================================
# ✅ FIXED: Base class with conflict resolution
# ============================================================================

# Create a custom metadata instance with conflict handling
metadata = MetaData()

# Base class
class Base:
    """Base class with conflict resolution"""
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Handle table conflicts during class creation"""
        super().__init_subclass__(**kwargs)
        
        # Add extend_existing=True to all table args if not present
        if hasattr(cls, '__table_args__'):
            if isinstance(cls.__table_args__, dict):
                if 'extend_existing' not in cls.__table_args__:
                    cls.__table_args__['extend_existing'] = True
            elif isinstance(cls.__table_args__, tuple):
                # Convert tuple to dict format
                args = list(cls.__table_args__)
                table_kwargs = {}
                
                # Extract dict from tuple if present
                for item in args:
                    if isinstance(item, dict):
                        table_kwargs.update(item)
                        args.remove(item)
                        break
                
                # Add extend_existing
                table_kwargs['extend_existing'] = True
                
                # Rebuild tuple
                cls.__table_args__ = tuple(args) + (table_kwargs,)
        else:
            # Add table args if not present
            cls.__table_args__ = {'extend_existing': True}

# Create declarative base with enhanced functionality
Base = declarative_base(
    metadata=metadata,
    cls=Base
)

# ============================================================================
# 🔧 CRITICAL FIX: Session configuration with proper async support
# ============================================================================

# Synchronous session for regular operations (uses psycopg2)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔧 CRITICAL FIX: Asynchronous session with asyncpg support
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 🔧 CRITICAL: Prevents greenlet_spawn errors
    autocommit=False,
    autoflush=False
)

# ============================================================================
# ✅ FIXED: Table creation functions with proper error handling
# ============================================================================

def create_tables_sync():
    """
    Create tables using synchronous engine with conflict resolution
    """
    try:
        logger.info("🗂️ Creating database tables (synchronous)...")
        
        # Use synchronous engine for table creation
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        if "already defined" in str(e) or "already exists" in str(e):
            logger.warning("⚠️ Table conflicts detected, attempting resolution...")
            
            try:
                # Method 1: Clear metadata and recreate
                logger.info("🔄 Clearing metadata and recreating tables...")
                Base.metadata.clear()
                
                # Recreate tables
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Tables recreated successfully after clearing metadata")
                return True
                
            except Exception as retry_error:
                logger.warning(f"⚠️ Metadata clearing failed: {retry_error}")
                
                try:
                    # Method 2: Drop and recreate all tables (CAUTION: This deletes data!)
                    logger.warning("🚨 Attempting full table recreation (data will be lost)")
                    Base.metadata.drop_all(bind=engine)
                    Base.metadata.create_all(bind=engine)
                    logger.info("✅ Tables recreated successfully after drop/create")
                    return True
                    
                except Exception as final_error:
                    logger.error(f"❌ All table creation methods failed: {final_error}")
                    return False
        else:
            logger.error(f"❌ Database table creation failed: {e}")
            return False

async def create_tables_async():
    """
    Create tables using asynchronous engine with asyncpg
    """
    try:
        logger.info("🗂️ Creating database tables (asynchronous with asyncpg)...")
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully (async with asyncpg)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Async table creation failed: {e}")
        return False

# ============================================================================
# ✅ FIXED: Database dependency functions
# ============================================================================

def get_db() -> Session:
    """
    Synchronous database dependency for FastAPI (uses psycopg2)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncSession:
    """
    Asynchronous database dependency for FastAPI (uses asyncpg)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 🔧 CRITICAL FIX: Add alias for backward compatibility
get_async_session = get_async_db

# ============================================================================
# ✅ FIXED: Database utility functions
# ============================================================================

def test_connection():
    """
    Test database connection (sync with psycopg2)
    """
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✅ Sync database connection test successful (psycopg2)")
            return True
    except Exception as e:
        logger.error(f"❌ Sync database connection test failed: {e}")
        return False

async def test_async_connection():
    """
    Test async database connection (asyncpg)
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Async database connection test successful (asyncpg)")
        return True
    except Exception as e:
        logger.error(f"❌ Async database connection test failed: {e}")
        return False

def get_table_info():
    """
    Get information about existing tables
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"📊 Found {len(tables)} existing tables: {tables}")
        return tables
    except Exception as e:
        logger.error(f"❌ Failed to get table info: {e}")
        return []

# ============================================================================
# ✅ FIXED: Database initialization function
# ============================================================================

def initialize_database():
    """
    Initialize database with comprehensive error handling
    """
    try:
        logger.info("🚀 Initializing database...")
        
        # Test both connections
        if not test_connection():
            logger.error("❌ Sync database connection failed")
            return False
        
        # Test async connection
        try:
            import asyncio
            asyncio.get_event_loop().run_until_complete(test_async_connection())
        except Exception as async_test_error:
            logger.warning(f"⚠️ Async connection test failed: {async_test_error}")
        
        # Get existing table info
        existing_tables = get_table_info()
        logger.info(f"📋 Existing tables: {len(existing_tables)}")
        
        # Create tables
        if create_tables_sync():
            logger.info("✅ Database initialization completed successfully")
            return True
        else:
            logger.error("❌ Database initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False

# ============================================================================
# ✅ FIXED: Cleanup function
# ============================================================================

def cleanup_database():
    """
    Cleanup database connections
    """
    try:
        engine.dispose()
        logger.info("✅ Sync database connections cleaned up")
    except Exception as e:
        logger.error(f"❌ Sync database cleanup error: {e}")

async def cleanup_async_database():
    """
    Cleanup async database connections
    """
    try:
        await async_engine.dispose()
        logger.info("✅ Async database connections cleaned up")
    except Exception as e:
        logger.error(f"❌ Async database cleanup error: {e}")

# ============================================================================
# 🆕 NEW: Driver verification function
# ============================================================================

def verify_database_drivers():
    """
    Verify that proper database drivers are being used
    """
    try:
        # Check sync driver
        sync_driver = engine.dialect.driver
        logger.info(f"🔍 Sync driver: {sync_driver}")
        
        # Check async driver  
        async_driver = async_engine.dialect.driver
        logger.info(f"🔍 Async driver: {async_driver}")
        
        # Verify correct drivers
        if sync_driver == "psycopg2" and async_driver == "asyncpg":
            logger.info("✅ Database drivers correctly configured")
            return True
        else:
            logger.warning(f"⚠️ Driver mismatch - Sync: {sync_driver}, Async: {async_driver}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Driver verification failed: {e}")
        return False

# ============================================================================
# ✅ EXPORTS
# ============================================================================

__all__ = [
    'engine',
    'async_engine', 
    'Base',
    'metadata',
    'SessionLocal',
    'AsyncSessionLocal',
    'get_db',
    'get_async_db',
    'get_async_session',  # 🔧 CRITICAL FIX: Export the alias
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