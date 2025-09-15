#!/usr/bin/env python3
"""
Check the actual table structure to see column types.
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_table_structure():
    """Check actual column types in the database"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Try Railway's internal database URL
        database_url = os.environ.get('DATABASE_PRIVATE_URL') 
        
    if not database_url:
        logger.error("No database URL found in environment variables")
        return False
        
    # Convert to async URL if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        
    logger.info(f"Connecting to database...")
    
    # Create engine
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            logger.info("Checking actual table structure...")
            
            # Check actual column types
            result = await conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    udt_name,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = 'campaigns' 
                AND column_name IN ('campaign_type', 'status')
                ORDER BY column_name;
            """))
            
            logger.info("Current campaigns table column types:")
            for row in result:
                logger.info(f"  {row.column_name}: {row.data_type} (udt_name: {row.udt_name}) DEFAULT {row.column_default}")
            
            # Check if enum types still exist
            enum_result = await conn.execute(text("""
                SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname;
            """))
            
            enum_types = [row.typname for row in enum_result]
            if enum_types:
                logger.warning(f"Enum types still exist: {enum_types}")
            else:
                logger.info("No enum types found in database")
                
            return True
            
    except Exception as e:
        logger.error(f"Check failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(check_table_structure())
    if success:
        logger.info("Table structure check completed")
    else:
        logger.error("Table structure check failed")
        exit(1)