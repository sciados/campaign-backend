-- ============================================================================
-- DATABASE VERIFICATION SCRIPT
-- Run this in Railway's pgAdmin to verify everything is configured correctly
-- ============================================================================

-- 1. Check if scraped_images table exists
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'scraped_images'
) AS scraped_images_table_exists;

-- 2. If table exists, show its structure
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'scraped_images'
ORDER BY ordinal_position;

-- 3. Check indexes on scraped_images
SELECT
    indexname AS index_name,
    indexdef AS definition
FROM pg_indexes
WHERE tablename = 'scraped_images';

-- 4. Count rows in scraped_images (should be 0 initially)
SELECT COUNT(*) AS row_count FROM scraped_images;

-- 5. Verify other important tables exist
SELECT
    table_name,
    CASE
        WHEN table_name = 'users' THEN '✓ Users table'
        WHEN table_name = 'campaigns' THEN '✓ Campaigns table'
        WHEN table_name = 'companies' THEN '✓ Companies table'
        WHEN table_name = 'scraped_images' THEN '✓ Scraped images table'
        ELSE table_name
    END as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('users', 'campaigns', 'companies', 'scraped_images')
ORDER BY table_name;

-- 6. Verify users have subscription_tier column
SELECT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'users'
    AND column_name = 'subscription_tier'
) AS users_has_subscription_tier;

-- 7. Check database connection count (should be low with NullPool)
SELECT
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active_connections,
    count(*) FILTER (WHERE state = 'idle') as idle_connections
FROM pg_stat_activity
WHERE datname = current_database();

-- ============================================================================
-- EXPECTED RESULTS:
-- 1. scraped_images_table_exists: true
-- 2. Should show ~18 columns (id, campaign_id, user_id, r2_path, etc.)
-- 3. Should show 4-5 indexes
-- 4. row_count: 0
-- 5. Should show all 4 tables
-- 6. users_has_subscription_tier: true
-- 7. total_connections: Should be < 10 with NullPool
-- ============================================================================
