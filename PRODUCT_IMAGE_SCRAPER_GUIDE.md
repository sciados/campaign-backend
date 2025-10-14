##

 Product Image Scraper - Complete Solution

## The Problem We Solved

**Original Challenge:**
- AI struggles to generate legible text in images (product labels, book titles)
- Mockup templates require separate label design step
- No way to extract existing product images from sales pages

**Our Solution:**
Extract high-quality product images directly from sales pages, save to Cloudflare R2, and use them for:
1. **Background composition** - Place on AI-generated scenes
2. **Reference images** - For creating similar designs
3. **Direct use** - Already has text/labels rendered perfectly

## Architecture

```
Sales Page URL
      ↓
┌─────────────────────────────────────┐
│ Product Image Scraper               │
│ - Fetch HTML                        │
│ - Extract all images                │
│ - Analyze & score quality           │
│ - Filter for product images         │
│ - Download best candidates          │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│ Smart Classification                │
│ - Hero images (main product)        │
│ - Product images (bottles, boxes)   │
│ - Lifestyle images (in-use shots)   │
│ - Quality scoring (0-100)           │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│ R2/Cloudflare Storage               │
│ campaigns/{id}/scraped-images/      │
│ - hero_01.jpg                       │
│ - product_02.png                    │
│ - lifestyle_03.jpg                  │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│ Database (PostgreSQL)               │
│ Table: scraped_images               │
│ - campaign_id                       │
│ - cdn_url, r2_path                  │
│ - width, height, quality_score      │
│ - is_hero, is_product, is_lifestyle │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│ Composite System Integration        │
│ Use scraped images as layers in:    │
│ - Background compositions           │
│ - Multi-product layouts             │
│ - Social media posts                │
└─────────────────────────────────────┘
```

## Key Features

### 1. Smart Image Detection

**Quality Scoring Algorithm (0-100 points):**

| Factor | Points | Criteria |
|--------|--------|----------|
| **Resolution** | 0-30 | 1MP+ = 30pts, 500K+ = 25pts, 250K+ = 20pts |
| **Aspect Ratio** | 0-20 | Square/portrait = 20pts (best for products) |
| **File Size** | 0-15 | 50KB-2MB = 15pts (sweet spot) |
| **Product Indicators** | 0-20 | Keywords in URL/alt/context |
| **Position** | 0-15 | Hero/featured = 15pts |

**Example Score:**
```
Image: supplement-bottle-hero.jpg
- 1200x1200 pixels → 30 points (high res)
- 1:1 aspect ratio → 20 points (square)
- 850KB file size → 15 points (optimized)
- URL contains "bottle" → 10 points
- Alt text: "Hero Product" → 15 points
Total Score: 90/100 ✅ Excellent
```

### 2. Image Classification

**Automatic Type Detection:**

```python
is_hero = True if:
  - Width >= 800px AND Height >= 600px
  - Context contains "hero", "main", "featured"
  - Parent element has hero/main class/ID

is_product = True if:
  - URL/alt/context contains: product, bottle, box, package
  - Typical product dimensions (square or portrait)

is_lifestyle = True if:
  - URL/alt/context contains: lifestyle, gym, hand, person
  - Shows product in real-world context
```

### 3. Duplicate Detection

Uses MD5 hashing to skip duplicate images:
```python
img_hash = hashlib.md5(image_bytes).hexdigest()
if img_hash in seen_hashes:
    skip()  # Don't save duplicates
```

### 4. Smart Filtering

**Automatically skips:**
- Icons and badges
- Social media buttons
- Tracking pixels
- Spinners/loaders
- Small logos
- Analytics images

**Skip patterns:**
```regex
pixel|tracker|analytics|icon|sprite|avatar|
social|loading|spinner|placeholder|1x1|blank|
widget|badge|favicon
```

## API Endpoints

### 1. Scrape Images from Sales Page

**POST /api/intelligence/product-images/scrape**

```json
Request:
{
  "campaign_id": "abc-123",
  "sales_page_url": "https://example.com/product-page",
  "max_images": 10,
  "auto_analyze": true
}

Response:
{
  "success": true,
  "campaign_id": "abc-123",
  "images_found": 47,
  "images_saved": 8,
  "images_skipped": 39,
  "images": [
    {
      "url": "https://r2.cloudflare.com/campaigns/abc-123/scraped-images/hero_01.jpg",
      "r2_path": "campaigns/abc-123/scraped-images/hero_01.jpg",
      "metadata": {
        "original_url": "https://example.com/product-hero.jpg",
        "width": 1200,
        "height": 1200,
        "file_size": 850000,
        "format": "jpeg",
        "alt_text": "Premium Supplement Bottle",
        "context": "Hero Product",
        "is_hero": true,
        "is_product": true,
        "is_lifestyle": false,
        "quality_score": 92.5,
        "scraped_at": "2025-01-14T10:30:00Z"
      }
    }
  ]
}
```

### 2. Analyze Page (Preview Mode)

**POST /api/intelligence/product-images/analyze-url**

Preview images without saving:

```json
Request:
{
  "url": "https://example.com/sales-page"
}

Response:
{
  "success": true,
  "url": "https://example.com/sales-page",
  "images_found": 47,
  "images_suitable": 12,
  "hero_images": 2,
  "product_images": 8,
  "lifestyle_images": 2,
  "top_images": [
    {
      "url": "https://example.com/hero.jpg",
      "width": 1200,
      "height": 1200,
      "quality_score": 92.5,
      "type": "hero"
    }
  ]
}
```

### 3. Get Campaign Images

**GET /api/intelligence/product-images/{campaign_id}**

```
Query Parameters:
- image_type: hero|product|lifestyle (optional filter)

Response:
{
  "success": true,
  "campaign_id": "abc-123",
  "images": [...],
  "count": 8
}
```

### 4. Delete Image

**DELETE /api/intelligence/product-images/{campaign_id}/{image_id}**

Removes from database and R2 storage.

## Integration with Composite System

### Use Case 1: Product on AI Background

```python
# Step 1: Scrape product image from sales page
scraped = await scraper.scrape_sales_page(
    url="https://example.com/sales-page",
    campaign_id="abc-123",
    max_images=5
)

# Step 2: Generate AI background
background = await ai_generator.generate(
    prompt="Modern gym interior with natural lighting"
)

# Step 3: Composite together
composite = await compositor.create_composite(
    background_url=background.url,
    foreground_layers=[{
        "image_url": scraped.images[0]["url"],  # Hero product image
        "position": {"anchor": "center"},
        "scale": 0.7
    }],
    text_layers=[{
        "text": "NEW PRODUCT",
        "position": {"anchor": "top_center"},
        "font_size": 72
    }]
)

# Result: Product with perfect label on professional background
```

### Use Case 2: Multi-Product Layout

```python
# Scrape multiple product images
hero_img = scraped_images[0]  # Main product
side_imgs = scraped_images[1:4]  # Supporting products

composite = await compositor.create_composite(
    background_url=ai_background,
    foreground_layers=[
        {"image_url": hero_img, "position": "center", "scale": 0.8},
        {"image_url": side_imgs[0], "position": "left", "scale": 0.3},
        {"image_url": side_imgs[1], "position": "right", "scale": 0.3},
    ]
)
```

### Use Case 3: Lifestyle Scene Enhancement

```python
# Use lifestyle image as base, add text overlay
lifestyle_img = [img for img in scraped if img["metadata"]["is_lifestyle"]][0]

composite = await compositor.create_composite(
    background_url=lifestyle_img["url"],
    text_layers=[
        {"text": "Transform Your Fitness", "position": "top_center", "font_size": 64},
        {"text": "Order Now", "position": "bottom_center", "font_size": 48}
    ]
)
```

## Database Schema

```sql
CREATE TABLE scraped_images (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    user_id UUID REFERENCES users(id),

    -- Storage
    r2_path VARCHAR NOT NULL,
    cdn_url VARCHAR NOT NULL,
    original_url VARCHAR,

    -- Properties
    width INT NOT NULL,
    height INT NOT NULL,
    file_size INT NOT NULL,
    format VARCHAR(10) NOT NULL,

    -- Metadata
    alt_text TEXT,
    context TEXT,
    quality_score FLOAT NOT NULL DEFAULT 0.0,

    -- Classification
    is_hero BOOLEAN DEFAULT FALSE,
    is_product BOOLEAN DEFAULT FALSE,
    is_lifestyle BOOLEAN DEFAULT FALSE,

    -- Usage tracking
    times_used INT DEFAULT 0,
    last_used_at TIMESTAMP,

    -- Additional metadata (JSONB)
    metadata JSONB,

    -- Timestamps
    scraped_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    -- Indexes
    INDEX idx_campaign_type (campaign_id, is_hero, is_product),
    INDEX idx_quality (quality_score),
    INDEX idx_usage (times_used)
);
```

## Usage Workflow

### Automatic (During Intelligence Analysis)

```python
# When user analyzes sales page URL
analysis = await intelligence_service.analyze_url(
    url="https://example.com/product",
    campaign_id="abc-123"
)

# Automatically scrape product images
background_tasks.add_task(
    scraper.scrape_sales_page,
    url=url,
    campaign_id=campaign_id,
    max_images=5
)

# User gets:
# 1. Intelligence analysis
# 2. Product images ready to use
```

### Manual (User-Triggered)

```python
# User clicks "Extract Product Images" button
result = await scraper.scrape_sales_page(
    url=user_provided_url,
    campaign_id=current_campaign,
    max_images=10
)

# Show user gallery of extracted images
# User selects which to use for composition
```

## Performance Optimization

### Async Processing
- All operations are async (aiohttp)
- Downloads images in parallel
- Non-blocking database writes

### Caching
- Duplicate detection (MD5 hashing)
- Skip already-scraped URLs
- Reuse images across campaigns

### Smart Filtering
- Skip tiny images early (file size check)
- Filter by patterns before downloading
- Limit analysis to first 50 images per page

## Cost Analysis

### Per Scraping Operation:
- **Bandwidth:** ~5-10MB download (images)
- **R2 Storage:** ~$0.015 per GB/month
- **Processing:** Minimal (CPU-bound analysis)
- **Total:** ~$0.001 per scrape

### Example Monthly Costs:
```
100 campaigns × 5 images each = 500 images
Average 500KB per image = 250MB storage
R2 Storage: $0.015 × 0.25 = $0.00375/month

Bandwidth (downloads): Free (R2 egress to Cloudflare CDN)

Total: < $0.01/month for 500 images
```

## Error Handling

```python
try:
    result = await scraper.scrape_sales_page(...)
except aiohttp.ClientError:
    # Network error
    return {"error": "Failed to fetch page"}
except PIL.UnidentifiedImageError:
    # Invalid image format
    return {"error": "Invalid image format"}
except Exception as e:
    # General error
    logger.error(f"Scraping failed: {e}")
    return {"error": "Scraping failed"}
```

## Future Enhancements

### Phase 2: AI-Powered Analysis
- Use computer vision to detect product type
- Extract brand colors from images
- Identify product category automatically
- Remove backgrounds automatically

### Phase 3: Smart Cropping
- Auto-crop to product focus
- Remove excess whitespace
- Center product in frame
- Standardize dimensions

### Phase 4: Batch Operations
- Scrape from multiple URLs
- Compare products across pages
- Generate variation sets
- A/B test different product shots

## Testing

### Unit Tests
```python
async def test_scrape_sales_page():
    async with ProductImageScraper() as scraper:
        result = await scraper.scrape_sales_page(
            url="https://test.com/product",
            campaign_id="test-123",
            max_images=5
        )
    assert result.success
    assert result.images_saved > 0

async def test_quality_scoring():
    scraper = ProductImageScraper()
    score = scraper._calculate_quality_score(
        width=1200, height=1200, file_size=800000,
        url="product-hero.jpg", alt_text="Main Product", context="Hero"
    )
    assert score >= 80  # High quality
```

### Integration Tests
```python
async def test_end_to_end_workflow():
    # 1. Scrape images
    scraped = await scraper.scrape_sales_page(...)

    # 2. Generate background
    background = await generator.generate(...)

    # 3. Composite
    final = await compositor.create_composite(
        background_url=background.url,
        foreground_layers=[{"image_url": scraped.images[0]["url"]}]
    )

    assert final.success
    assert final.image_url is not None
```

## Deployment Checklist

- [x] Product image scraper service created
- [x] API routes implemented
- [x] Database migration ready
- [x] R2 storage integration
- [x] Routes added to main app
- [ ] Run database migration
- [ ] Test with real sales pages
- [ ] Frontend integration
- [ ] User documentation

## Next Steps

1. **Run Migration:**
   ```bash
   alembic upgrade head
   ```

2. **Test Scraping:**
   ```bash
   curl -X POST https://api.campaignforge.com/api/intelligence/product-images/scrape \
     -H "Authorization: Bearer TOKEN" \
     -d '{
       "campaign_id": "test-123",
       "sales_page_url": "https://example.com/product",
       "max_images": 5
     }'
   ```

3. **Frontend Integration:**
   - Add "Extract Product Images" button to campaign page
   - Show gallery of scraped images
   - Allow selection for composite generation

---

**Status:** ✅ Ready to deploy
**Impact:** Solves text-in-image problem by using real product images
**Integration:** Works seamlessly with composite system
**Cost:** <$0.01/month for typical usage
