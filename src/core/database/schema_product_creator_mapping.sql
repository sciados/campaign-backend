-- Product Creator Mapping Schema
-- This allows funneling user analytics results to the correct Product Creators

-- Table to store product creator mappings
CREATE TABLE IF NOT EXISTS product_creator_mappings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    product_sku VARCHAR(255) NOT NULL,
    product_name VARCHAR(500),
    vendor_account VARCHAR(255),
    creator_user_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure unique mapping per platform/product
    UNIQUE (platform, product_sku),

    -- Foreign key to users table
    FOREIGN KEY (creator_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table to store aggregated analytics for creators
CREATE TABLE IF NOT EXISTS creator_product_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    creator_user_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    product_sku VARCHAR(255) NOT NULL,

    -- Aggregated metrics from all affiliates promoting this product
    total_affiliates INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.00,
    total_quantity INTEGER DEFAULT 0,
    avg_conversion_rate DECIMAL(5,2) DEFAULT 0.00,

    -- Time period for aggregation
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Raw analytics data from all affiliates
    affiliate_data JSONB DEFAULT '[]',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure unique aggregation per creator/platform/product/period
    UNIQUE (creator_user_id, platform, product_sku, period_start, period_end),

    -- Foreign keys
    FOREIGN KEY (creator_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_user_id, platform, product_sku) REFERENCES product_creator_mappings(creator_user_id, platform, product_sku)
);

-- Table to track affiliate performance for creator insights
CREATE TABLE IF NOT EXISTS affiliate_product_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    affiliate_user_id UUID NOT NULL,
    creator_user_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    product_sku VARCHAR(255) NOT NULL,

    -- Performance metrics for this affiliate
    sales INTEGER DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0.00,
    quantity INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,

    -- Performance period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Raw performance data
    performance_data JSONB DEFAULT '{}',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Ensure unique tracking per affiliate/creator/product/period
    UNIQUE (affiliate_user_id, creator_user_id, platform, product_sku, period_start, period_end),

    -- Foreign keys
    FOREIGN KEY (affiliate_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_user_id, platform, product_sku) REFERENCES product_creator_mappings(creator_user_id, platform, product_sku)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_product_creator_mappings_platform_sku ON product_creator_mappings(platform, product_sku);
CREATE INDEX IF NOT EXISTS idx_product_creator_mappings_creator ON product_creator_mappings(creator_user_id);
CREATE INDEX IF NOT EXISTS idx_creator_analytics_creator_platform ON creator_product_analytics(creator_user_id, platform);
CREATE INDEX IF NOT EXISTS idx_creator_analytics_period ON creator_product_analytics(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_affiliate_performance_affiliate ON affiliate_product_performance(affiliate_user_id);
CREATE INDEX IF NOT EXISTS idx_affiliate_performance_creator ON affiliate_product_performance(creator_user_id);

-- Comments
COMMENT ON TABLE product_creator_mappings IS 'Maps products to their creators for analytics funneling';
COMMENT ON TABLE creator_product_analytics IS 'Aggregated analytics for product creators from all their affiliates';
COMMENT ON TABLE affiliate_product_performance IS 'Individual affiliate performance data for creator insights';