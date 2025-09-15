#!/usr/bin/env python3
"""
Aggressive enum removal script - drops ALL enum types from the database.
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def drop_all_enums():
    """Drop ALL enum types from the database"""
    
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
    engine = create_async_engine(database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            logger.info("Dropping ALL enum types...")
            
            # Execute the aggressive enum drop
            await conn.execute(text("""
                DO $$ 
                DECLARE
                    enum_name text;
                BEGIN
                    -- Drop ALL enum types in the database
                    FOR enum_name IN 
                        SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname
                    LOOP
                        BEGIN
                            EXECUTE 'DROP TYPE IF EXISTS ' || enum_name || ' CASCADE';
                            RAISE NOTICE 'Dropped enum type: %', enum_name;
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE 'Could not drop enum type %: %', enum_name, SQLERRM;
                        END;
                    END LOOP;
                    
                    RAISE NOTICE 'All enum types removal completed!';
                END 
                $$;
            """))
            
            # Verify no enum types remain
            enum_result = await conn.execute(text("""
                SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname;
            """))
            
            remaining_enums = [row.typname for row in enum_result]
            if remaining_enums:
                logger.warning(f"WARNING: Still have enum types: {remaining_enums}")
                return False
            else:
                logger.info("SUCCESS: All enum types removed from database")
                return True
                
    except Exception as e:
        logger.error(f"Failed to drop enums: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(drop_all_enums())
    if success:
        logger.info("All enum types successfully dropped")
    else:
        logger.error("Failed to drop all enum types")
        exit(1)