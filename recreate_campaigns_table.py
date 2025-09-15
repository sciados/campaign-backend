#!/usr/bin/env python3
"""
RECREATE CAMPAIGNS TABLE: Drop and recreate with correct VARCHAR columns
Since there's no data to preserve, this is the cleanest approach.
"""

import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def recreate_campaigns_table():
    """Drop and recreate campaigns table with correct schema"""
    
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
            logger.info("RECREATING campaigns table...")
            
            # Step 1: Drop campaigns table completely (this will cascade to remove dependencies)
            await conn.execute(text("""
                DROP TABLE IF EXISTS campaigns CASCADE;
            """))
            logger.info("Dropped campaigns table")
            
            # Step 2: Drop any remaining enum types
            await conn.execute(text("DROP TYPE IF EXISTS campaigntypeenum CASCADE;"))
            await conn.execute(text("DROP TYPE IF EXISTS campaignstatusenum CASCADE;"))
            logger.info("Dropped enum types")
            
            # Step 3: Create new campaigns table with VARCHAR columns
            await conn.execute(text("""
                CREATE TABLE campaigns (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    campaign_type VARCHAR(50) NOT NULL DEFAULT 'content_marketing',
                    status VARCHAR(20) NOT NULL DEFAULT 'draft',
                    user_id UUID NOT NULL,
                    company_id UUID NOT NULL,
                    target_audience TEXT,
                    goals JSONB,
                    settings JSONB,
                    intelligence_id UUID,
                    intelligence_status VARCHAR(50) DEFAULT 'pending',
                    workflow_step VARCHAR(50) DEFAULT 'INITIAL',
                    workflow_data JSONB,
                    is_workflow_complete BOOLEAN DEFAULT FALSE,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    revenue INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    launched_at TIMESTAMP WITH TIME ZONE,
                    completed_at TIMESTAMP WITH TIME ZONE
                );
            """))
            logger.info("Created new campaigns table with VARCHAR columns")
            
            # Step 4: Add foreign key constraints (if users/companies tables exist)
            try:
                await conn.execute(text("""
                    ALTER TABLE campaigns 
                    ADD CONSTRAINT fk_campaigns_user_id 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                """))
                logger.info("Added user_id foreign key constraint")
            except Exception as e:
                logger.warning(f"Could not add user_id FK (users table may not exist): {e}")
            
            try:
                await conn.execute(text("""
                    ALTER TABLE campaigns 
                    ADD CONSTRAINT fk_campaigns_company_id 
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;
                """))
                logger.info("Added company_id foreign key constraint")
            except Exception as e:
                logger.warning(f"Could not add company_id FK (companies table may not exist): {e}")
            
            # Step 5: Add check constraints for valid values
            await conn.execute(text("""
                ALTER TABLE campaigns 
                ADD CONSTRAINT check_campaign_type 
                CHECK (campaign_type IN (
                    'email_sequence', 
                    'social_media', 
                    'content_marketing', 
                    'affiliate_promotion', 
                    'product_launch'
                ))
            """))
            
            await conn.execute(text("""
                ALTER TABLE campaigns 
                ADD CONSTRAINT check_status 
                CHECK (status IN (
                    'draft', 
                    'active', 
                    'paused', 
                    'completed', 
                    'archived'
                ))
            """))
            logger.info("Added check constraints for valid values")
            
            # Step 6: Verify the final state
            result = await conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    udt_name,
                    column_default,
                    is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'campaigns' 
                AND column_name IN ('campaign_type', 'status')
                ORDER BY column_name;
            """))
            
            logger.info("FINAL COLUMN STATE:")
            for row in result:
                logger.info(f"  {row.column_name}: {row.data_type} (udt_name: {row.udt_name}) DEFAULT {row.column_default} NULL: {row.is_nullable}")
            
            # Check remaining enum types
            enum_result = await conn.execute(text("""
                SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname;
            """))
            
            enum_types = [row.typname for row in enum_result]
            if enum_types:
                logger.warning(f"Remaining enum types: {enum_types}")
            else:
                logger.info("SUCCESS: No enum types remain - CAMPAIGNS TABLE RECREATED!")
                
            return True
            
    except Exception as e:
        logger.error(f"Table recreation failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(recreate_campaigns_table())
    if success:
        logger.info("CAMPAIGNS TABLE RECREATION COMPLETED SUCCESSFULLY")
    else:
        logger.error("CAMPAIGNS TABLE RECREATION FAILED")
        exit(1)