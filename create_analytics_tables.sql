-- Create analytics tables for multi-platform analytics system
-- Date: 2025-09-20

-- Create platform_analytics table
CREATE TABLE IF NOT EXISTS platform_analytics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    raw_data JSONB NOT NULL DEFAULT '{}',
    processed_metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

-- Create product_analytics table
CREATE TABLE IF NOT EXISTS product_analytics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, platform, product_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_platform_analytics_user_id ON platform_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_platform_analytics_platform ON platform_analytics(platform);
CREATE INDEX IF NOT EXISTS idx_platform_analytics_updated_at ON platform_analytics(updated_at);

CREATE INDEX IF NOT EXISTS idx_product_analytics_user_id ON product_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_product_analytics_platform ON product_analytics(platform);
CREATE INDEX IF NOT EXISTS idx_product_analytics_product_id ON product_analytics(product_id);
CREATE INDEX IF NOT EXISTS idx_product_analytics_updated_at ON product_analytics(updated_at);

-- Add comments
COMMENT ON TABLE platform_analytics IS 'Stores aggregated analytics data from various affiliate platforms';
COMMENT ON TABLE product_analytics IS 'Stores individual product performance metrics across platforms';

COMMENT ON COLUMN platform_analytics.user_id IS 'UUID of the user who owns this analytics data';
COMMENT ON COLUMN platform_analytics.platform IS 'Platform name (clickbank, jvzoo, warriorplus, etc.)';
COMMENT ON COLUMN platform_analytics.raw_data IS 'Raw API response data from the platform';
COMMENT ON COLUMN platform_analytics.processed_metrics IS 'Normalized metrics for cross-platform comparison';

COMMENT ON COLUMN product_analytics.user_id IS 'UUID of the user promoting this product';
COMMENT ON COLUMN product_analytics.platform IS 'Platform where this product is listed';
COMMENT ON COLUMN product_analytics.product_id IS 'Platform-specific product identifier';
COMMENT ON COLUMN product_analytics.product_name IS 'Human-readable product name';
COMMENT ON COLUMN product_analytics.metrics IS 'Product-specific performance metrics';