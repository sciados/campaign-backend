-- ============================================================================
-- SIMPLE DATABASE VERIFICATION
-- Run each query separately in Railway's pgAdmin Query Tool
-- ============================================================================

-- Query 1: List all tables in database
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected: campaigns, companies, scraped_images, users, and other tables

-- ============================================================================

-- Query 2: Check if scraped_images table exists
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'scraped_images'
        ) THEN 'scraped_images table EXISTS ✓'
        ELSE 'scraped_images table MISSING ✗'
    END as status;

-- Expected: "scraped_images table EXISTS ✓"

-- ============================================================================

-- Query 3: Show scraped_images table structure
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'scraped_images'
ORDER BY ordinal_position;

-- Expected: ~18 columns including id, campaign_id, user_id, r2_path, cdn_url, etc.

-- ============================================================================

-- Query 4: Check scraped_images indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'scraped_images';

-- Expected: 4-5 indexes including primary key and campaign_id index

-- ============================================================================

-- Query 5: Count rows in scraped_images
SELECT COUNT(*) as row_count FROM scraped_images;

-- Expected: 0 (table is empty since you deleted all content)

-- ============================================================================

-- Query 6: Check if users table has subscription_tier column
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name = 'subscription_tier'
        ) THEN 'subscription_tier column EXISTS ✓'
        ELSE 'subscription_tier column MISSING ✗'
    END as status;

-- Expected: "subscription_tier column EXISTS ✓"

-- ============================================================================

-- Query 7: Check database connections (should be low with NullPool)
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle
FROM pg_stat_activity
WHERE datname = current_database();

-- Expected: total_connections < 10 (thanks to NullPool fix)

-- ============================================================================
-- If any table is missing, run the migration SQL from PGADMIN_MIGRATION_005_CLEAN.sql
-- ============================================================================
