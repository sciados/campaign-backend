#!/usr/bin/env python3
"""
Manual migration runner for Railway deployment
Runs the database migration to create the missing enum types
"""

import os
import sys
import asyncio
import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def run_migration():
    """Run the database migration manually"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not found")
        return False
        
    # Convert to async URL
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    print(f"🔗 Connecting to database...")
    
    try:
        # Create engine
        engine = create_async_engine(database_url)
        
        async with engine.begin() as conn:
            print("✅ Connected to database")
            
            # Check if enums already exist
            print("🔍 Checking if enum types exist...")
            
            check_enums = text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'campaignstatusenum'
                ) as status_enum_exists,
                EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'campaigntypeenum'
                ) as type_enum_exists;
            """)
            
            result = await conn.execute(check_enums)
            row = result.fetchone()
            
            if row and row.status_enum_exists and row.type_enum_exists:
                print("✅ Enum types already exist - no migration needed")
                return True
            
            print("🚀 Creating enum types...")
            
            # Create the enum types
            create_status_enum = text("""
                DO $$ BEGIN
                    CREATE TYPE campaignstatusenum AS ENUM (
                        'draft', 'active', 'paused', 'completed', 'archived'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """)
            
            create_type_enum = text("""
                DO $$ BEGIN
                    CREATE TYPE campaigntypeenum AS ENUM (
                        'email_sequence', 'social_media', 'content_marketing', 
                        'affiliate_promotion', 'product_launch'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """)
            
            await conn.execute(create_status_enum)
            print("✅ Created campaignstatusenum type")
            
            await conn.execute(create_type_enum)
            print("✅ Created campaigntypeenum type")
            
            # Update table columns if campaigns table exists
            print("🔧 Updating campaigns table columns...")
            
            update_columns = text("""
                DO $$ BEGIN
                    -- Check if campaigns table exists
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'campaigns') THEN
                        -- Update status column if it's not already an enum
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'campaigns' 
                            AND column_name = 'status' 
                            AND udt_name = 'campaignstatusenum'
                        ) THEN
                            ALTER TABLE campaigns 
                            ALTER COLUMN status TYPE campaignstatusenum 
                            USING status::campaignstatusenum;
                        END IF;
                        
                        -- Update campaign_type column if it's not already an enum
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'campaigns' 
                            AND column_name = 'campaign_type' 
                            AND udt_name = 'campaigntypeenum'
                        ) THEN
                            ALTER TABLE campaigns 
                            ALTER COLUMN campaign_type TYPE campaigntypeenum 
                            USING campaign_type::campaigntypeenum;
                        END IF;
                    END IF;
                END $$;
            """)
            
            await conn.execute(update_columns)
            print("✅ Updated campaigns table columns")
            
            # Verify the migration worked
            verify_query = text("""
                SELECT 
                    EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaignstatusenum') as status_exists,
                    EXISTS (SELECT 1 FROM pg_type WHERE typname = 'campaigntypeenum') as type_exists;
            """)
            
            result = await conn.execute(verify_query)
            row = result.fetchone()
            
            if row and row.status_exists and row.type_exists:
                print("🎉 Migration completed successfully!")
                print("✅ Both enum types now exist in the database")
                return True
            else:
                print("❌ Migration verification failed")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("🚀 Starting Railway database migration...")
    success = asyncio.run(run_migration())
    
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)