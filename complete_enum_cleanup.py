#!/usr/bin/env python3
"""
Complete enum cleanup script for PostgreSQL database.
Removes all enum types and constraints, converts all enum columns to varchar.
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def complete_enum_cleanup():
    """Remove all enum types and constraints, convert all columns to varchar"""
    
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
            logger.info("🧹 Starting complete enum cleanup...")
            
            # Execute the complete cleanup
            await conn.execute(text("""
                DO $$ 
                DECLARE
                    enum_name text;
                BEGIN
                    -- Step 1: Convert all enum columns to varchar
                    RAISE NOTICE '🔧 Converting enum columns to varchar...';
                    
                    -- Check if campaigns table exists and convert columns
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                        RAISE NOTICE 'Processing campaigns table...';
                        
                        -- Convert campaign_type column
                        BEGIN
                            ALTER TABLE campaigns 
                            ALTER COLUMN campaign_type TYPE VARCHAR(50) 
                            USING campaign_type::text;
                            
                            ALTER TABLE campaigns 
                            ALTER COLUMN campaign_type SET DEFAULT 'content_marketing';
                            
                            RAISE NOTICE '✅ campaigns.campaign_type converted to VARCHAR(50)';
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE '⚠️  campaigns.campaign_type: %', SQLERRM;
                        END;
                        
                        -- Convert status column  
                        BEGIN
                            ALTER TABLE campaigns 
                            ALTER COLUMN status TYPE VARCHAR(50) 
                            USING status::text;
                            
                            ALTER TABLE campaigns 
                            ALTER COLUMN status SET DEFAULT 'draft';
                            
                            RAISE NOTICE '✅ campaigns.status converted to VARCHAR(50)';
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE '⚠️  campaigns.status: %', SQLERRM;
                        END;
                    END IF;
                    
                    -- Check for other tables that might have enum columns
                    -- Convert any other enum columns found
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaign_intelligence') THEN
                        BEGIN
                            ALTER TABLE campaign_intelligence 
                            ALTER COLUMN analysis_status TYPE VARCHAR(50) 
                            USING analysis_status::text;
                            
                            RAISE NOTICE '✅ campaign_intelligence.analysis_status converted to VARCHAR(50)';
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE '⚠️  campaign_intelligence.analysis_status: %', SQLERRM;
                        END;
                    END IF;
                    
                    -- Step 2: Drop all enum types
                    RAISE NOTICE '🗑️  Dropping enum types...';
                    
                    -- Drop enum types if they exist
                    FOR enum_name IN 
                        SELECT typname FROM pg_type 
                        WHERE typtype = 'e' 
                        AND typname IN ('campaigntypeenum', 'campaignstatusenum', 'analysisstatusenum')
                    LOOP
                        BEGIN
                            EXECUTE 'DROP TYPE IF EXISTS ' || enum_name || ' CASCADE';
                            RAISE NOTICE '🗑️  Dropped enum type: %', enum_name;
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE '⚠️  Could not drop enum type %: %', enum_name, SQLERRM;
                        END;
                    END LOOP;
                    
                    -- Step 3: Remove any remaining enum constraints or dependencies
                    RAISE NOTICE '🧽 Cleaning up constraints...';
                    
                    -- Remove check constraints that might reference enum values
                    BEGIN
                        -- This will remove any check constraints on the converted columns
                        ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_campaign_type_check;
                        ALTER TABLE campaigns DROP CONSTRAINT IF EXISTS campaigns_status_check;
                        RAISE NOTICE '✅ Removed enum check constraints';
                    EXCEPTION
                        WHEN OTHERS THEN 
                            RAISE NOTICE '⚠️  Constraint cleanup: %', SQLERRM;
                    END;
                    
                    RAISE NOTICE '🎉 Complete enum cleanup finished!';
                END 
                $$;
            """))
            
            # Verify the changes
            result = await conn.execute(text("""
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    character_maximum_length,
                    column_default
                FROM information_schema.columns 
                WHERE table_name IN ('campaigns', 'campaign_intelligence')
                AND column_name IN ('status', 'campaign_type', 'analysis_status')
                ORDER BY table_name, column_name;
            """))
            
            logger.info("\n📊 Column information after cleanup:")
            for row in result:
                logger.info(f"  {row.table_name}.{row.column_name}: {row.data_type}({row.character_maximum_length}) DEFAULT {row.column_default}")
            
            # Check for remaining enum types
            enum_result = await conn.execute(text("""
                SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname;
            """))
            
            remaining_enums = [row.typname for row in enum_result]
            if remaining_enums:
                logger.warning(f"⚠️  Remaining enum types: {remaining_enums}")
            else:
                logger.info("✅ No enum types remaining in database")
                
            logger.info("🎉 Complete database enum cleanup completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(complete_enum_cleanup())
    if success:
        logger.info("✅ Complete enum cleanup script completed successfully")
    else:
        logger.error("❌ Complete enum cleanup script failed")
        exit(1)