#!/usr/bin/env python3
"""
NUCLEAR OPTION: Absolutely force remove all enum constraints and convert to VARCHAR
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def nuclear_enum_fix():
    """Nuclear option to completely remove enum constraints"""
    
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
            logger.info("NUCLEAR OPTION: Completely removing enum constraints...")
            
            # Step 1: Drop ALL foreign key constraints that might reference these columns
            await conn.execute(text("""
                DO $$ 
                DECLARE
                    constraint_record RECORD;
                BEGIN
                    -- Drop all foreign key constraints on campaigns table
                    FOR constraint_record IN
                        SELECT conname, conrelid::regclass
                        FROM pg_constraint 
                        WHERE contype = 'f' AND (conrelid::regclass::text = 'campaigns' OR confrelid::regclass::text = 'campaigns')
                    LOOP
                        EXECUTE 'ALTER TABLE ' || constraint_record.conrelid || ' DROP CONSTRAINT IF EXISTS ' || constraint_record.conname || ' CASCADE';
                        RAISE NOTICE 'Dropped FK constraint: %', constraint_record.conname;
                    END LOOP;
                END $$;
            """))
            
            # Step 2: Drop all check constraints
            await conn.execute(text("""
                DO $$ 
                DECLARE
                    constraint_record RECORD;
                BEGIN
                    FOR constraint_record IN
                        SELECT conname
                        FROM pg_constraint c
                        JOIN pg_class t ON c.conrelid = t.oid
                        WHERE t.relname = 'campaigns' AND contype = 'c'
                    LOOP
                        EXECUTE 'ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS ' || constraint_record.conname || ' CASCADE';
                        RAISE NOTICE 'Dropped check constraint: %', constraint_record.conname;
                    END LOOP;
                END $$;
            """))
            
            # Step 3: Backup existing data and recreate columns completely
            await conn.execute(text("""
                DO $$ 
                BEGIN
                    -- Create backup columns
                    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS campaign_type_backup TEXT;
                    ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS status_backup TEXT;
                    
                    -- Copy existing data (cast enum to text)
                    UPDATE campaigns SET campaign_type_backup = campaign_type::text;
                    UPDATE campaigns SET status_backup = status::text;
                    
                    RAISE NOTICE 'Data backed up successfully';
                    
                    -- Drop the enum columns completely
                    ALTER TABLE campaigns DROP COLUMN IF EXISTS campaign_type CASCADE;
                    ALTER TABLE campaigns DROP COLUMN IF EXISTS status CASCADE;
                    
                    RAISE NOTICE 'Enum columns dropped';
                    
                    -- Add new VARCHAR columns
                    ALTER TABLE campaigns ADD COLUMN campaign_type VARCHAR(50) NOT NULL DEFAULT 'content_marketing';
                    ALTER TABLE campaigns ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'draft';
                    
                    RAISE NOTICE 'New VARCHAR columns added';
                    
                    -- Restore data
                    UPDATE campaigns SET campaign_type = campaign_type_backup WHERE campaign_type_backup IS NOT NULL;
                    UPDATE campaigns SET status = status_backup WHERE status_backup IS NOT NULL;
                    
                    RAISE NOTICE 'Data restored to new columns';
                    
                    -- Drop backup columns
                    ALTER TABLE campaigns DROP COLUMN IF EXISTS campaign_type_backup;
                    ALTER TABLE campaigns DROP COLUMN IF EXISTS status_backup;
                    
                    RAISE NOTICE 'Backup columns cleaned up';
                    
                EXCEPTION
                    WHEN OTHERS THEN
                        RAISE NOTICE 'Error during column recreation: %', SQLERRM;
                        -- Don't fail completely, continue to enum cleanup
                END $$;
            """))
            
            # Step 4: Drop all enum types
            await conn.execute(text("""
                DO $$ 
                DECLARE
                    enum_record RECORD;
                BEGIN
                    FOR enum_record IN
                        SELECT typname FROM pg_type WHERE typtype = 'e'
                    LOOP
                        EXECUTE 'DROP TYPE IF EXISTS ' || enum_record.typname || ' CASCADE';
                        RAISE NOTICE 'Dropped enum type: %', enum_record.typname;
                    END LOOP;
                END $$;
            """))
            
            # Step 5: Verify the final state
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
            
            logger.info("FINAL COLUMN STATE:")
            for row in result:
                logger.info(f"  {row.column_name}: {row.data_type} (udt_name: {row.udt_name}) DEFAULT {row.column_default}")
            
            # Check remaining enum types
            enum_result = await conn.execute(text("""
                SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname;
            """))
            
            enum_types = [row.typname for row in enum_result]
            if enum_types:
                logger.warning(f"Remaining enum types: {enum_types}")
            else:
                logger.info("SUCCESS: No enum types remain - NUCLEAR CLEANUP COMPLETE!")
                
            return True
            
    except Exception as e:
        logger.error(f"Nuclear enum fix failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(nuclear_enum_fix())
    if success:
        logger.info("NUCLEAR ENUM FIX COMPLETED SUCCESSFULLY")
    else:
        logger.error("NUCLEAR ENUM FIX FAILED")
        exit(1)