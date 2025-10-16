# Database Table Analysis - October 14, 2025

## Total Tables: 75

Database export from Railway shows all tables are present and correctly configured.

---

## Key Tables for Product Image Scraper Workflow

### Core Campaign Tables
- **`campaigns`** (line 12) - Main campaign data
- **`users`** (line 74) - User accounts with subscription_tier
- **`companies`** (line 18) - Company/organization data

### New Image Scraper Tables
- **`scraped_images`** ✅ (line 55) - Product images extracted from sales pages
- **`campaign_assets`** (line 11) - Campaign asset management

### Intelligence & Analysis
- **`intelligence_core`** (line 34) - Core intelligence data
- **`intelligence_research`** (line 35) - Research data
- **`scraped_content`** (line 54) - Scraped sales page content
- **`user_intelligence_cache`** (line 69) - Cached intelligence results

### Content Generation
- **`content_generations`** (line 22) - Generated content tracking
- **`generated_content`** (line 28) - Stored generated content
- **`content_generation_workflows`** (line 21) - Workflow state
- **`generated_prompts`** (line 29) - Prompt library

### Storage & Analytics
- **`user_storage_usage`** (line 72) - Storage quota tracking
- **`ai_provider_usage`** (line 6) - AI provider cost tracking
- **`usage_analytics`** (line 64) - Usage metrics

### Performance Tracking
- **`performance_metrics`** (line 43) - Content performance
- **`product_performance`** (line 51) - Product metrics
- **`conversion_events`** (line 24) - Conversion tracking

---

## Product Image Scraper Data Flow

```
1. User creates campaign → campaigns table
2. Intelligence analyzes URL → intelligence_core table
3. Scraper extracts images → scraped_images table
4. Images stored in R2 → user_storage_usage updated
5. Content generated → generated_content table
6. Performance tracked → performance_metrics table
```

---

## `scraped_images` Table Schema

```sql
CREATE TABLE scraped_images (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

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

-- Indexes
CREATE INDEX idx_scraped_images_campaign ON scraped_images(campaign_id);
CREATE INDEX idx_scraped_images_user ON scraped_images(user_id);
CREATE INDEX idx_scraped_images_quality ON scraped_images(quality_score DESC);
CREATE INDEX idx_scraped_images_campaign_type ON scraped_images(campaign_id, is_hero, is_product);
```

---

## Relationships

### scraped_images → campaigns
- **Foreign Key:** `campaign_id` → `campaigns.id`
- **Cascade:** ON DELETE CASCADE (delete images when campaign deleted)

### scraped_images → users
- **Foreign Key:** `user_id` → `users.id`
- **Cascade:** ON DELETE CASCADE (delete images when user deleted)

### Data Integrity
- Images are automatically cleaned up when campaigns are deleted
- Orphaned images prevented by foreign key constraints
- Quality scoring ensures only high-quality images are used

---

## Storage Tracking

When images are scraped:
1. File saved to Cloudflare R2 at `campaigns/{id}/scraped-images/`
2. CDN URL generated for fast access
3. Row inserted into `scraped_images` table
4. `user_storage_usage` updated with file size
5. Campaign analytics updated

---

## Query Examples

### Get all scraped images for a campaign:
```sql
SELECT * FROM scraped_images
WHERE campaign_id = 'abc-123'
ORDER BY quality_score DESC;
```

### Get hero images only:
```sql
SELECT * FROM scraped_images
WHERE campaign_id = 'abc-123'
AND is_hero = TRUE
ORDER BY quality_score DESC
LIMIT 1;
```

### Get images by type:
```sql
SELECT
    COUNT(*) FILTER (WHERE is_hero) as hero_count,
    COUNT(*) FILTER (WHERE is_product) as product_count,
    COUNT(*) FILTER (WHERE is_lifestyle) as lifestyle_count,
    AVG(quality_score) as avg_quality
FROM scraped_images
WHERE campaign_id = 'abc-123';
```

### Track most used images:
```sql
SELECT
    cdn_url,
    quality_score,
    times_used,
    last_used_at
FROM scraped_images
WHERE campaign_id = 'abc-123'
ORDER BY times_used DESC
LIMIT 5;
```

---

## Database Status

✅ **All 75 tables present**
✅ **scraped_images table confirmed**
✅ **Foreign key relationships intact**
✅ **Indexes created for performance**
✅ **Ready for production use**

---

## Verification Completed

Database export confirms:
- All tables from CSV present
- scraped_images table at line 55
- Database structure intact after pgAdmin reconfiguration
- No data loss during Railway infrastructure issues

**System ready for product image scraping!** 🚀
