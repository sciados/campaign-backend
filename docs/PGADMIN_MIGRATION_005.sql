-- ============================================================================
-- Migration 005: Add scraped_images table
-- Run this in pgAdmin SQL Query Tool
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create scraped_images table
CREATE TABLE IF NOT EXISTS scraped_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Storage locations
    r2_path VARCHAR NOT NULL,
    cdn_url VARCHAR NOT NULL,
    original_url VARCHAR,

    -- Image properties
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    file_size INTEGER NOT NULL,  -- bytes
    format VARCHAR(10) NOT NULL,  -- jpg, png, webp

    -- Metadata
    alt_text TEXT,
    context TEXT,  -- Surrounding text on page
    quality_score FLOAT NOT NULL DEFAULT 0.0,

    -- Classification flags
    is_hero BOOLEAN DEFAULT FALSE NOT NULL,
    is_product BOOLEAN DEFAULT FALSE NOT NULL,
    is_lifestyle BOOLEAN DEFAULT FALSE NOT NULL,

    -- Usage tracking
    times_used INTEGER DEFAULT 0 NOT NULL,
    last_used_at TIMESTAMP,

    -- Additional metadata (JSON)
    metadata JSONB,

    -- Timestamps
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_scraped_images_campaign
    ON scraped_images(campaign_id);

CREATE INDEX IF NOT EXISTS idx_scraped_images_user
    ON scraped_images(user_id);

CREATE INDEX IF NOT EXISTS idx_scraped_images_campaign_type
    ON scraped_images(campaign_id, is_hero, is_product);

CREATE INDEX IF NOT EXISTS idx_scraped_images_quality
    ON scraped_images(quality_score DESC);

CREATE INDEX IF NOT EXISTS idx_scraped_images_usage
    ON scraped_images(times_used DESC);

CREATE INDEX IF NOT EXISTS idx_scraped_images_hero
    ON scraped_images(is_hero) WHERE is_hero = TRUE;

CREATE INDEX IF NOT EXISTS idx_scraped_images_product
    ON scraped_images(is_product) WHERE is_product = TRUE;

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_scraped_images_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS scraped_images_updated_at_trigger ON scraped_images;
CREATE TRIGGER scraped_images_updated_at_trigger
    BEFORE UPDATE ON scraped_images
    FOR EACH ROW
    EXECUTE FUNCTION update_scraped_images_updated_at();

-- Add comments for documentation
COMMENT ON TABLE scraped_images IS 'Product images extracted from sales pages';
COMMENT ON COLUMN scraped_images.quality_score IS 'Quality score 0-100 based on resolution, context, relevance';
COMMENT ON COLUMN scraped_images.is_hero IS 'Main/hero product image (large, prominent)';
COMMENT ON COLUMN scraped_images.is_product IS 'Product-focused image (bottle, box, package)';
COMMENT ON COLUMN scraped_images.is_lifestyle IS 'Lifestyle/contextual image (product in use)';
COMMENT ON COLUMN scraped_images.times_used IS 'How many times this image was used in composites';

-- Verify table was created successfully
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'scraped_images'
ORDER BY ordinal_position;

-- Verify indexes were created
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'scraped_images';

-- Show final summary
SELECT
    'Migration 005 completed successfully!' AS status,
    COUNT(*) AS total_columns
FROM information_schema.columns
WHERE table_name = 'scraped_images';

-- ============================================================================
-- OPTIONAL: Insert test data (remove this section in production)
-- ============================================================================

/*
-- Example test data (uncomment to test)
INSERT INTO scraped_images (
    campaign_id,
    user_id,
    r2_path,
    cdn_url,
    original_url,
    width,
    height,
    file_size,
    format,
    alt_text,
    context,
    quality_score,
    is_hero,
    is_product,
    metadata
) VALUES (
    (SELECT id FROM campaigns LIMIT 1),  -- Use first campaign
    (SELECT id FROM users LIMIT 1),      -- Use first user
    'campaigns/test-123/scraped-images/hero_01.jpg',
    'https://r2.campaignforge.com/campaigns/test-123/scraped-images/hero_01.jpg',
    'https://example.com/product-image.jpg',
    1200,
    1200,
    850000,
    'jpeg',
    'Premium Supplement Bottle',
    'Hero Product Section',
    92.5,
    TRUE,
    TRUE,
    '{"source": "sales_page", "scraper_version": "1.0"}'::JSONB
);
*/

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'scraped_images'
) AS table_exists;

-- Count rows (should be 0 initially)
SELECT COUNT(*) AS row_count FROM scraped_images;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
