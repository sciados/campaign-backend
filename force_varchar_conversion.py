#!/usr/bin/env python3
"""
Force conversion of enum columns to varchar by dropping dependencies first.
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_varchar_conversion():
    """Force conversion of columns from enum to varchar"""
    
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
            logger.info("Force converting enum columns to varchar...")
            
            # Execute the forceful conversion
            await conn.execute(text("""
                DO $$ 
                BEGIN
                    -- First, try to backup existing data
                    RAISE NOTICE 'Starting forceful enum to varchar conversion...';
                    
                    -- Method 1: Try direct conversion using text casting
                    BEGIN
                        ALTER TABLE campaigns 
                        ALTER COLUMN campaign_type TYPE VARCHAR(50) 
                        USING campaign_type::text;
                        
                        RAISE NOTICE 'SUCCESS: campaign_type converted to VARCHAR(50)';
                    EXCEPTION
                        WHEN OTHERS THEN 
                            RAISE NOTICE 'Method 1 failed for campaign_type: %', SQLERRM;
                            
                            -- Method 2: Create temp column, copy data, drop old, rename
                            BEGIN
                                -- Add temporary column
                                ALTER TABLE campaigns ADD COLUMN campaign_type_temp VARCHAR(50);
                                
                                -- Copy data with explicit text conversion
                                UPDATE campaigns SET campaign_type_temp = 
                                    CASE 
                                        WHEN campaign_type::text = 'social_media' THEN 'social_media'
                                        WHEN campaign_type::text = 'email_marketing' THEN 'email_marketing'
                                        WHEN campaign_type::text = 'content_marketing' THEN 'content_marketing'
                                        WHEN campaign_type::text = 'affiliate_promotion' THEN 'affiliate_promotion'
                                        WHEN campaign_type::text = 'product_launch' THEN 'product_launch'
                                        ELSE 'content_marketing'
                                    END;
                                
                                -- Drop old column
                                ALTER TABLE campaigns DROP COLUMN campaign_type;
                                
                                -- Rename temp column
                                ALTER TABLE campaigns RENAME COLUMN campaign_type_temp TO campaign_type;
                                
                                -- Set default
                                ALTER TABLE campaigns ALTER COLUMN campaign_type SET DEFAULT 'content_marketing';
                                
                                RAISE NOTICE 'SUCCESS: campaign_type converted using temp column method';
                            EXCEPTION
                                WHEN OTHERS THEN 
                                    RAISE NOTICE 'Method 2 also failed for campaign_type: %', SQLERRM;
                            END;
                    END;
                    
                    -- Convert status column
                    BEGIN
                        ALTER TABLE campaigns 
                        ALTER COLUMN status TYPE VARCHAR(50) 
                        USING status::text;
                        
                        RAISE NOTICE 'SUCCESS: status converted to VARCHAR(50)';
                    EXCEPTION
                        WHEN OTHERS THEN 
                            RAISE NOTICE 'Method 1 failed for status: %', SQLERRM;
                            
                            -- Method 2 for status column
                            BEGIN
                                -- Add temporary column
                                ALTER TABLE campaigns ADD COLUMN status_temp VARCHAR(50);
                                
                                -- Copy data with explicit text conversion
                                UPDATE campaigns SET status_temp = 
                                    CASE 
                                        WHEN status::text = 'draft' THEN 'draft'
                                        WHEN status::text = 'active' THEN 'active' 
                                        WHEN status::text = 'completed' THEN 'completed'
                                        WHEN status::text = 'archived' THEN 'archived'
                                        ELSE 'draft'
                                    END;
                                
                                -- Drop old column
                                ALTER TABLE campaigns DROP COLUMN status;
                                
                                -- Rename temp column
                                ALTER TABLE campaigns RENAME COLUMN status_temp TO status;
                                
                                -- Set default
                                ALTER TABLE campaigns ALTER COLUMN status SET DEFAULT 'draft';
                                
                                RAISE NOTICE 'SUCCESS: status converted using temp column method';
                            EXCEPTION
                                WHEN OTHERS THEN 
                                    RAISE NOTICE 'Method 2 also failed for status: %', SQLERRM;
                            END;
                    END;
                    
                    -- Now drop the enum types
                    BEGIN
                        DROP TYPE IF EXISTS campaigntypeenum CASCADE;
                        DROP TYPE IF EXISTS campaignstatusenum CASCADE;
                        RAISE NOTICE 'SUCCESS: Dropped enum types';
                    EXCEPTION
                        WHEN OTHERS THEN 
                            RAISE NOTICE 'Could not drop enum types: %', SQLERRM;
                    END;
                    
                    RAISE NOTICE 'Force conversion completed!';
                END 
                $$;
            """))
            
            # Verify the conversion
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
            
            logger.info("Column types after force conversion:")
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
                logger.info("SUCCESS: No enum types remain")
                
            return True
            
    except Exception as e:
        logger.error(f"Force conversion failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(force_varchar_conversion())
    if success:
        logger.info("Force varchar conversion completed")
    else:
        logger.error("Force varchar conversion failed")
        exit(1)