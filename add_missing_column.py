#!/usr/bin/env python3
"""
Add missing messaging_focus column to campaigns table
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_missing_column():
    """Add messaging_focus column to campaigns table"""
    
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
            logger.info("Adding missing messaging_focus column...")
            
            # Add the missing column
            await conn.execute(text("""
                ALTER TABLE campaigns 
                ADD COLUMN IF NOT EXISTS messaging_focus TEXT;
            """))
            logger.info("Added messaging_focus column")
            
            # Verify the column was added
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'campaigns' 
                AND column_name = 'messaging_focus';
            """))
            
            column_info = result.fetchone()
            if column_info:
                logger.info(f"✅ messaging_focus column confirmed: {column_info.data_type}, nullable: {column_info.is_nullable}")
            else:
                logger.error("❌ messaging_focus column not found after addition")
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"Failed to add column: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(add_missing_column())
    if success:
        logger.info("MISSING COLUMN ADDED SUCCESSFULLY")
    else:
        logger.error("FAILED TO ADD MISSING COLUMN")
        exit(1)