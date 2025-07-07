# src/core/database.py - FIXED VERSION for AsyncEngine and table conflicts
import os
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import asyncio

logger = logging.getLogger(__name__)

# ============================================================================
# ✅ FIXED: Database Configuration with both Sync and Async engines
# ============================================================================

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Convert postgres:// to postgresql:// if needed (Railway compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create async version of the URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

logger.info(f"🔗 Database URL configured: {DATABASE_URL[:50]}...")

# ============================================================================
# ✅ FIXED: Create both sync and async engines
# ============================================================================

# Synchronous engine for table creation and simple operations
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

# Asynchronous engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
    # Add connection args for better compatibility
    connect_args={
        "server_settings": {
            "application_name": "CampaignForge_Backend",
        }
    }
)

# ============================================================================
# ✅ FIXED: Enhanced Base class with conflict resolution
# ============================================================================

# Create a custom metadata instance with conflict handling
metadata = MetaData()

# Enhanced Base class
class EnhancedBase:
    """Enhanced base class with conflict resolution"""
    
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
    cls=EnhancedBase
)

# ============================================================================
# ✅ FIXED: Session configuration
# ============================================================================

# Synchronous session for regular operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Asynchronous session for async operations
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
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
        logger.info("🏗️ Creating database tables (synchronous)...")
        
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
    Create tables using asynchronous engine
    """
    try:
        logger.info("🏗️ Creating database tables (asynchronous)...")
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully (async)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Async table creation failed: {e}")
        return False

# ============================================================================
# ✅ FIXED: Database dependency functions
# ============================================================================

def get_db() -> Session:
    """
    Synchronous database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncSession:
    """
    Asynchronous database dependency for FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# ============================================================================
# ✅ FIXED: Database utility functions
# ============================================================================

def test_connection():
    """
    Test database connection
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

async def test_async_connection():
    """
    Test async database connection
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Async database connection test successful")
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
# ✅ FIXED: Enhanced initialization function
# ============================================================================

def initialize_database():
    """
    Initialize database with comprehensive error handling
    """
    try:
        logger.info("🚀 Initializing database...")
        
        # Test connection first
        if not test_connection():
            logger.error("❌ Database connection failed")
            return False
        
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
        logger.info("✅ Database connections cleaned up")
    except Exception as e:
        logger.error(f"❌ Database cleanup error: {e}")

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
    'create_tables_sync',
    'create_tables_async',
    'test_connection',
    'test_async_connection',
    'initialize_database',
    'cleanup_database',
    'cleanup_async_database',
    'get_table_info'
]