-- Migration: Create Analytics Tables
-- Description: Create tables for multi-platform analytics and rename ClickBank fields
-- Date: 2025-09-20

-- Create platform_analytics table for storing aggregated analytics from all platforms
CREATE TABLE IF NOT EXISTS platform_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform VARCHAR(50) NOT NULL,
    raw_data JSONB NOT NULL DEFAULT '{}',
    processed_metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

-- Create product_analytics table for storing individual product performance
CREATE TABLE IF NOT EXISTS product_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform VARCHAR(50) NOT NULL,
    product_id VARCHAR(255) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform, product_id)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_platform_analytics_user_platform ON platform_analytics(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_platform_analytics_platform ON platform_analytics(platform);
CREATE INDEX IF NOT EXISTS idx_platform_analytics_updated_at ON platform_analytics(updated_at);

CREATE INDEX IF NOT EXISTS idx_product_analytics_user_platform ON product_analytics(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_product_analytics_platform ON product_analytics(platform);
CREATE INDEX IF NOT EXISTS idx_product_analytics_product_id ON product_analytics(product_id);
CREATE INDEX IF NOT EXISTS idx_product_analytics_updated_at ON product_analytics(updated_at);

-- Update ClickBank table to use new field names (rename clerk_key to api_key)
DO $$
BEGIN
    -- Check if the old column exists before renaming
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'clickbank_accounts'
        AND column_name = 'clerk_key'
    ) THEN
        -- Rename the column
        ALTER TABLE clickbank_accounts RENAME COLUMN clerk_key TO api_key;
    END IF;
END
$$;

-- Add comment to tables
COMMENT ON TABLE platform_analytics IS 'Stores aggregated analytics data from various affiliate platforms';
COMMENT ON TABLE product_analytics IS 'Stores individual product performance metrics across platforms';

-- Add comment to updated ClickBank table
COMMENT ON COLUMN clickbank_accounts.api_key IS 'User API key for ClickBank (renamed from clerk_key as of August 2023)';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON platform_analytics TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON product_analytics TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE platform_analytics_id_seq TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE product_analytics_id_seq TO your_app_user;