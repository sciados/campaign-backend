#!/usr/bin/env python3
"""
Database migration script to convert enum columns to varchar.
This fixes the type mismatch between PostgreSQL enum types and SQLAlchemy String columns.
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_enum_columns():
    """Convert enum columns to varchar to match SQLAlchemy String columns"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Try Railway's internal database URL
        database_url = os.environ.get('DATABASE_PRIVATE_URL') 
        
    if not database_url:
        logger.error("No database URL found in environment variables")
        return False
        
    logger.info(f"Connecting to database...")
    
    # Create engine
    engine = create_async_engine(database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            logger.info("🔧 Converting enum columns to varchar...")
            
            # Execute the conversion
            await conn.execute(text("""
                DO $$ 
                BEGIN
                    -- Check if campaigns table exists
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                        RAISE NOTICE 'Converting campaigns table columns...';
                        
                        -- Convert status column from enum to varchar
                        BEGIN
                            ALTER TABLE campaigns 
                            ALTER COLUMN status TYPE VARCHAR(50) 
                            USING status::text;
                            
                            ALTER TABLE campaigns 
                            ALTER COLUMN status SET DEFAULT 'draft';
                            
                            RAISE NOTICE '✅ Converted status column to VARCHAR(50)';
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE '⚠️  Status column: %', SQLERRM;
                        END;
                        
                        -- Convert campaign_type column from enum to varchar
                        BEGIN
                            ALTER TABLE campaigns 
                            ALTER COLUMN campaign_type TYPE VARCHAR(50) 
                            USING campaign_type::text;
                            
                            ALTER TABLE campaigns 
                            ALTER COLUMN campaign_type SET DEFAULT 'content_marketing';
                            
                            RAISE NOTICE '✅ Converted campaign_type column to VARCHAR(50)';
                        EXCEPTION
                            WHEN OTHERS THEN 
                                RAISE NOTICE '⚠️  Campaign_type column: %', SQLERRM;
                        END;
                        
                        RAISE NOTICE '✅ Column conversion completed successfully!';
                    ELSE
                        RAISE NOTICE '❌ Campaigns table not found';
                    END IF;
                END 
                $$;
            """))
            
            # Verify the changes
            result = await conn.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = 'campaigns' 
                AND column_name IN ('status', 'campaign_type')
                ORDER BY column_name;
            """))
            
            logger.info("\n📊 Column information after conversion:")
            for row in result:
                logger.info(f"  {row.column_name}: {row.data_type}({row.character_maximum_length}) DEFAULT {row.column_default}")
                
            logger.info("🎉 Database migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(fix_enum_columns())
    if success:
        logger.info("✅ Migration script completed successfully")
    else:
        logger.error("❌ Migration script failed")
        exit(1)