# Product Image Scraper - Complete Database Persistence Flow

## Overview

Scraped product images are now saved to **BOTH** Cloudflare R2 storage **AND** the PostgreSQL database for complete data persistence and easy retrieval.

---

## Complete Flow Diagram

```
User Request (POST /scrape)
    ↓
┌─────────────────────────────────────────────────────────┐
│ Product Image Scraper Service                           │
│ 1. Fetch HTML from sales page                           │
│ 2. Extract & analyze images                             │
│ 3. Score quality (0-100)                                 │
│ 4. Classify type (hero/product/lifestyle)               │
│ 5. Download image bytes                                  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│ Cloudflare R2 Storage (PRIMARY)                         │
│ - Upload image bytes to R2                              │
│ - Path: campaigns/{id}/scraped-images/hero_01.jpg       │
│ - Returns: CDN URL for fast delivery                    │
│ - Status: IMMEDIATE                                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│ Background Task (NON-BLOCKING)                          │
│ FastAPI BackgroundTasks adds database write             │
│ - Doesn't block API response                            │
│ - Runs after response sent to user                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│ PostgreSQL Database - scraped_images Table              │
│ INSERT INTO scraped_images (                            │
│   id, campaign_id, user_id,                             │
│   r2_path, cdn_url, original_url,                       │
│   width, height, file_size, format,                     │
│   quality_score, is_hero, is_product,                   │
│   metadata, scraped_at                                  │
│ )                                                        │
│ Status: PERSISTED                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Why Both R2 AND Database?

### Cloudflare R2 (Blob Storage)
**Purpose:** Store actual image files
- Fast CDN delivery
- Optimized for binary data
- Cheaper than database storage
- Direct browser access via HTTPS

### PostgreSQL Database (Metadata)
**Purpose:** Track image metadata and enable queries
- **Searchable** - Find by campaign, type, quality
- **Relational** - Link to campaigns and users
- **Queryable** - Get hero images, best quality, most used
- **Analytics** - Track usage, performance metrics
- **Foreign Keys** - Auto-delete when campaign deleted

---

## Database Schema

```sql
CREATE TABLE scraped_images (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign keys (CASCADE delete)
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Storage references
    r2_path VARCHAR NOT NULL,              -- campaigns/{id}/scraped/hero_01.jpg
    cdn_url VARCHAR NOT NULL,              -- https://cdn.../hero_01.jpg
    original_url VARCHAR,                  -- Original source URL

    -- Image properties
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    file_size INTEGER NOT NULL,
    format VARCHAR(10) NOT NULL,           -- jpg, png, webp

    -- Classification & Quality
    quality_score FLOAT DEFAULT 0.0,       -- 0-100 score
    is_hero BOOLEAN DEFAULT FALSE,
    is_product BOOLEAN DEFAULT FALSE,
    is_lifestyle BOOLEAN DEFAULT FALSE,

    -- Context
    alt_text TEXT,
    context TEXT,

    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,

    -- Additional metadata (JSONB)
    metadata JSONB,

    -- Timestamps
    scraped_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_scraped_images_campaign ON scraped_images(campaign_id);
CREATE INDEX idx_scraped_images_user ON scraped_images(user_id);
CREATE INDEX idx_scraped_images_quality ON scraped_images(quality_score DESC);
CREATE INDEX idx_scraped_images_campaign_type ON scraped_images(campaign_id, is_hero, is_product);
```

---

## API Usage

### 1. Scrape Images (Saves to R2 + Database)

```bash
POST /api/intelligence/product-images/scrape
Authorization: Bearer {token}
Content-Type: application/json

{
  "campaign_id": "abc-123",
  "sales_page_url": "https://example.com/product",
  "max_images": 10
}

Response:
{
  "success": true,
  "campaign_id": "abc-123",
  "images_found": 47,
  "images_saved": 8,     # Saved to BOTH R2 AND database
  "images_skipped": 39,
  "images": [
    {
      "url": "https://cdn.campaignforge.com/.../hero_01.jpg",  # CDN URL
      "r2_path": "campaigns/abc-123/scraped-images/hero_01.jpg",
      "metadata": {
        "width": 1200,
        "height": 1200,
        "quality_score": 92.5,
        "is_hero": true,
        "is_product": true,
        "format": "jpeg"
      }
    }
  ]
}
```

**What Happens:**
1. ✅ Images downloaded and uploaded to R2 (immediate)
2. ✅ Response returned to user with CDN URLs
3. ✅ Background task saves metadata to database (async)

---

### 2. Retrieve Scraped Images (From Database)

```bash
GET /api/intelligence/product-images/{campaign_id}?image_type=hero
Authorization: Bearer {token}

Response:
{
  "success": true,
  "campaign_id": "abc-123",
  "count": 3,
  "images": [
    {
      "id": "uuid-here",
      "campaign_id": "abc-123",
      "user_id": "user-uuid",
      "r2_path": "campaigns/abc-123/scraped-images/hero_01.jpg",
      "cdn_url": "https://cdn.campaignforge.com/.../hero_01.jpg",
      "original_url": "https://example.com/product-image.jpg",
      "width": 1200,
      "height": 1200,
      "file_size": 850000,
      "format": "jpeg",
      "quality_score": 92.5,
      "is_hero": true,
      "is_product": true,
      "is_lifestyle": false,
      "times_used": 0,
      "last_used_at": null,
      "scraped_at": "2025-10-14T23:45:00Z",
      "created_at": "2025-10-14T23:45:01Z"
    }
  ]
}
```

**Query Options:**
- `?image_type=hero` - Only hero images
- `?image_type=product` - Only product images
- `?image_type=lifestyle` - Only lifestyle images
- No filter - All images (sorted by quality_score DESC)

---

### 3. Delete Image (From Database + R2)

```bash
DELETE /api/intelligence/product-images/{campaign_id}/{image_id}
Authorization: Bearer {token}

Response:
{
  "success": true,
  "message": "Image deleted successfully"
}
```

**What Happens:**
1. ✅ Verifies image belongs to campaign
2. ✅ Deletes from database (immediate)
3. ⏳ TODO: Delete from R2 (background task)

---

## Query Examples

### Get Hero Image for Campaign
```python
from src.intelligence.repositories.scraped_image_repository import ScrapedImageRepository

# Get best hero image
images = await ScrapedImageRepository.get_by_campaign(
    db=db,
    campaign_id="abc-123",
    image_type="hero"
)
hero_image = images[0] if images else None  # Sorted by quality_score DESC
```

### Get Campaign Image Statistics
```python
stats = await ScrapedImageRepository.get_stats(db=db, campaign_id="abc-123")
# Returns:
# {
#   "total_count": 8,
#   "hero_count": 2,
#   "product_count": 5,
#   "lifestyle_count": 1,
#   "avg_quality": 85.3,
#   "max_quality": 92.5,
#   "total_size_mb": 6.8
# }
```

### Track Image Usage
```python
# Increment usage when image is used in composite
await ScrapedImageRepository.increment_usage(db=db, image_id="image-uuid")

# Get most used images
most_used = await ScrapedImageRepository.get_most_used(
    db=db,
    campaign_id="abc-123",
    limit=5
)
```

---

## Data Consistency

### Automatic Cleanup (CASCADE DELETE)
When a campaign is deleted:
```sql
DELETE FROM campaigns WHERE id = 'abc-123';
```

**Automatic cascade:**
1. ✅ All rows in `scraped_images` with `campaign_id = 'abc-123'` are deleted
2. ⏳ TODO: R2 files should also be deleted (background cleanup job)

### Orphan Prevention
Foreign key constraints prevent:
- ❌ Images referencing non-existent campaigns
- ❌ Images referencing non-existent users
- ❌ Orphaned database records

---

## Performance Optimization

### Background Tasks
Database writes run in background to avoid blocking API responses:
```python
# API responds immediately with R2 URLs
background_tasks.add_task(_save_image_to_db, ...)

# User receives response ~2-5 seconds
# Database write happens async in next 1-2 seconds
```

### Indexes
Queries are optimized with indexes on:
- `campaign_id` - Fast campaign lookups
- `quality_score DESC` - Best images first
- `(campaign_id, is_hero, is_product)` - Filtered queries

### NullPool Connection Management
No connection pooling = No connection exhaustion:
```python
# Each query opens/closes connection immediately
# No idle connections eating up Railway's limit
```

---

## Error Handling

### R2 Upload Fails
- ❌ Image not saved to R2
- ❌ No database record created (skipped)
- ✅ Other images continue processing

### Database Write Fails
- ✅ Image already in R2 (accessible via CDN)
- ❌ No database metadata (won't appear in queries)
- 🔍 Error logged for debugging
- ✅ API response still successful (R2 URLs returned)

### Consistency Check
If database is missing records but R2 has files:
1. Check logs for database write errors
2. Re-run scraper (will create new database records)
3. R2 deduplication prevents duplicate files

---

## Testing

### Verify Both Storage Locations

1. **Scrape Images:**
```bash
curl -X POST https://api.campaignforge.com/api/intelligence/product-images/scrape \
  -H "Authorization: Bearer TOKEN" \
  -d '{"campaign_id": "test-123", "sales_page_url": "https://example.com"}'
```

2. **Check R2 (via CDN URL):**
```bash
curl https://cdn.campaignforge.com/campaigns/test-123/scraped-images/hero_01.jpg
# Should return image file
```

3. **Check Database:**
```bash
curl https://api.campaignforge.com/api/intelligence/product-images/test-123 \
  -H "Authorization: Bearer TOKEN"
# Should return JSON with image metadata
```

4. **Verify in pgAdmin:**
```sql
SELECT * FROM scraped_images WHERE campaign_id = 'test-123';
-- Should show rows with r2_path, cdn_url, quality_score, etc.
```

---

## Status

✅ **COMPLETE AND DEPLOYED**

- ✅ R2 storage integration
- ✅ Database model created
- ✅ Repository CRUD operations
- ✅ Background task persistence
- ✅ GET endpoint (fetch from DB)
- ✅ DELETE endpoint (remove from DB)
- ✅ Foreign key constraints
- ✅ Cascade deletes
- ✅ Quality scoring
- ✅ Usage tracking
- ⏳ TODO: R2 deletion on DELETE endpoint

**Ready for production use!** 🚀

Images are now fully persisted and queryable via the database while being served fast via Cloudflare CDN.
