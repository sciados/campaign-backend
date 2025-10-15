-- ============================================================================
-- Migration 005: Add scraped_images table
-- COMPLETE SQL - Run in pgAdmin Query Tool
-- ============================================================================

-- Step 1: Enable UUID extension (required for uuid_generate_v4())
-- This is safe to run even if already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 2: Create scraped_images table
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
    file_size INTEGER NOT NULL,
    format VARCHAR(10) NOT NULL,

    -- Metadata
    alt_text TEXT,
    context TEXT,
    quality_score FLOAT NOT NULL DEFAULT 0.0,

    -- Classification flags
    is_hero BOOLEAN DEFAULT FALSE NOT NULL,
    is_product BOOLEAN DEFAULT FALSE NOT NULL,
    is_lifestyle BOOLEAN DEFAULT FALSE NOT NULL,

    -- Usage tracking
    times_used INTEGER DEFAULT 0 NOT NULL,
    last_used_at TIMESTAMP,

    -- Additional metadata
    metadata JSONB,

    -- Timestamps
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Step 3: Create indexes
CREATE INDEX IF NOT EXISTS idx_scraped_images_campaign ON scraped_images(campaign_id);
CREATE INDEX IF NOT EXISTS idx_scraped_images_user ON scraped_images(user_id);
CREATE INDEX IF NOT EXISTS idx_scraped_images_quality ON scraped_images(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_scraped_images_campaign_type ON scraped_images(campaign_id, is_hero, is_product);

-- Step 4: Create updated_at trigger
CREATE OR REPLACE FUNCTION update_scraped_images_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS scraped_images_updated_at_trigger ON scraped_images;

CREATE TRIGGER scraped_images_updated_at_trigger
    BEFORE UPDATE ON scraped_images
    FOR EACH ROW
    EXECUTE FUNCTION update_scraped_images_updated_at();

-- Step 5: Verify migration
SELECT
    'Table created successfully!' AS status,
    COUNT(*) AS column_count
FROM information_schema.columns
WHERE table_name = 'scraped_images';

SELECT
    indexname AS index_name
FROM pg_indexes
WHERE tablename = 'scraped_images';
