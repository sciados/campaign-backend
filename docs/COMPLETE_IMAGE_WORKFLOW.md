# Complete Image Generation Workflow

## Overview

CampaignForge now has a complete, modular image generation pipeline that combines:
1. **Product Image Extraction** from sales pages (solves AI text rendering problem)
2. **AI Background Generation** for custom scenes
3. **Image Composition** to combine multiple layers with text overlays
4. **Mockup Templates** via Dynamic Mockups API (custom PSD uploads)

## The Problem We Solved

**Challenge:** AI struggles to generate legible text in images (product labels, book titles, etc.)

**Solution:** Extract existing product images with perfect text/labels from sales pages, then composite them onto AI-generated backgrounds.

## Complete Workflow

### Step 1: Campaign Intelligence Analysis
```
User creates campaign → Analyzes sales page URL
↓
Intelligence Engine extracts:
- Product information
- Target audience
- Marketing angles
- Sales page URL
```

### Step 2: Product Image Extraction (Automated)
```
Sales Page URL
↓
Product Image Scraper Service
- Fetches HTML from sales page
- Extracts all images from page
- Analyzes each image (quality, type, context)
- Scores images 0-100 based on:
  * Resolution (0-30 pts)
  * Aspect ratio (0-20 pts)
  * File size (0-15 pts)
  * Product indicators (0-20 pts)
  * Position/context (0-15 pts)
- Classifies images:
  * Hero images (main product)
  * Product images (bottles, boxes)
  * Lifestyle images (in-use shots)
- Downloads best images
- Saves to Cloudflare R2 storage
- Stores metadata in database
↓
Result: Campaign has 5-10 high-quality product images ready to use
```

**API Endpoint:**
```bash
POST /api/intelligence/product-images/scrape
{
  "campaign_id": "abc-123",
  "sales_page_url": "https://example.com/product",
  "max_images": 10
}

Response:
{
  "success": true,
  "images_found": 47,
  "images_saved": 8,
  "images_skipped": 39,
  "images": [
    {
      "url": "https://cdn.campaignforge.com/campaigns/abc/scraped/hero_01.jpg",
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

### Step 3: Background Generation
```
User requests image generation
↓
AI Service (Flux/Stable Diffusion/Midjourney)
- Generates background scene based on:
  * Product type
  * Target audience
  * Marketing angle
  * User preferences
↓
Result: High-quality AI-generated background
```

**Example Prompts:**
- Supplement: "Modern gym interior with natural lighting, minimalist, professional"
- eBook: "Cozy reading nook with warm lighting, wooden bookshelf"
- Software: "Modern tech workspace, dual monitors, clean desk"

### Step 4: Image Composition
```
Inputs:
- Background image (AI-generated)
- Product image (scraped from sales page)
- Text layers (headline, call-to-action)
- Optional: badges, logos, additional elements

Composite Image Service:
1. Downloads background image
2. Downloads foreground product image
3. Positions product using anchor system:
   - center, top_center, bottom_center
   - left_center, right_center
   - top_left, top_right, bottom_left, bottom_right
4. Applies transformations:
   - Scale (resize)
   - Opacity (transparency)
   - Blend mode (normal, multiply, screen)
5. Renders text layers with:
   - Custom fonts
   - Colors and stroke
   - Shadows for readability
   - Position anchoring
6. Exports final composite
7. Saves to R2 storage
↓
Result: Professional composite image ready for ads
```

**API Endpoint:**
```bash
POST /api/content/composite/create
{
  "campaign_id": "abc-123",
  "background_url": "https://cdn.campaignforge.com/ai/background_01.jpg",
  "foreground_layers": [
    {
      "image_url": "https://cdn.campaignforge.com/campaigns/abc/scraped/hero_01.jpg",
      "position": {"anchor": "center", "offset_y": -50},
      "scale": 0.7,
      "opacity": 1.0,
      "z_index": 1
    }
  ],
  "text_layers": [
    {
      "text": "Transform Your Health",
      "position": {"anchor": "top_center", "offset_y": 100},
      "font_size": 72,
      "color": "#FFFFFF",
      "stroke": {"width": 3, "color": "#000000"},
      "shadow": {"blur": 10, "offset_x": 2, "offset_y": 2, "color": "#00000080"}
    },
    {
      "text": "ORDER NOW",
      "position": {"anchor": "bottom_center", "offset_y": -100},
      "font_size": 48,
      "color": "#FFD700"
    }
  ],
  "output_format": "jpeg",
  "quality": 95
}

Response:
{
  "success": true,
  "composite_url": "https://cdn.campaignforge.com/campaigns/abc/composites/final_001.jpg",
  "r2_path": "campaigns/abc-123/composites/final_001.jpg",
  "width": 1920,
  "height": 1080
}
```

### Step 5: Mockup Generation (Optional)
```
For physical product mockups:

User selects mockup template
↓
Dynamic Mockups API
- Applies product image to mockup template
- Renders 3D product visualization
- Returns high-quality mockup
↓
Result: Professional product mockup
```

**Templates Available:**
- Supplement bottles (front, angled, hand-holding)
- Product boxes
- Book covers
- eBook mockups
- Software screenshots

## Architecture

### Modular Design
```
┌─────────────────────────────────────────────────────┐
│         Intelligence Engine                         │
│  - URL Analysis                                     │
│  - Product Information Extraction                   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│    Product Image Scraper (NEW)                      │
│  - Fetch HTML from sales page                       │
│  - Extract & analyze images                         │
│  - Quality scoring (0-100)                          │
│  - Classification (hero/product/lifestyle)          │
│  - Save to R2 storage                               │
│  - Database persistence                             │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│         AI Image Generation                         │
│  - Flux, Stable Diffusion, Midjourney               │
│  - Background scenes                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│    Composite Image Service (NEW)                    │
│  - Layer management                                 │
│  - Position & transform                             │
│  - Text rendering                                   │
│  - Export & storage                                 │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│         Dynamic Mockups API (Optional)              │
│  - Custom PSD templates                             │
│  - Professional mockup rendering                    │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
                FINAL IMAGE
```

### Communication Pattern
- **URL-based**: Services communicate via image URLs
- **Stateless**: Each service is independent
- **Async**: All operations are non-blocking
- **Cached**: R2/CDN for fast delivery

## Database Schema

### scraped_images Table
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
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    file_size INTEGER NOT NULL,
    format VARCHAR(10) NOT NULL,

    -- Metadata
    alt_text TEXT,
    context TEXT,
    quality_score FLOAT NOT NULL,

    -- Classification
    is_hero BOOLEAN DEFAULT FALSE,
    is_product BOOLEAN DEFAULT FALSE,
    is_lifestyle BOOLEAN DEFAULT FALSE,

    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,

    metadata JSONB,
    scraped_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Use Cases

### Use Case 1: Facebook Ad Creation
```
1. User analyzes supplement sales page
2. System extracts hero product image (supplement bottle)
3. User generates AI background (gym interior)
4. System composites:
   - AI gym background
   - Scraped supplement bottle (center, scaled 0.7)
   - Text: "TRANSFORM YOUR BODY" (top)
   - Text: "ORDER NOW" (bottom)
5. Export 1200x1200 Facebook ad
```

### Use Case 2: Email Header
```
1. User extracts lifestyle image from sales page
2. System composites:
   - Lifestyle image as background
   - Dark overlay (opacity 0.5)
   - White headline text with shadow
   - CTA button graphic
3. Export 600x300 email header
```

### Use Case 3: Instagram Story
```
1. Extract product image from sales page
2. Generate AI background (vibrant colors)
3. Composite vertical 1080x1920:
   - AI background (full bleed)
   - Product image (center top, scaled 0.6)
   - Text overlays (bottom)
   - Swipe-up graphic
4. Export for Instagram Stories
```

### Use Case 4: Multi-Product Layout
```
1. Extract 3 product images from sales page
2. Generate neutral background
3. Composite:
   - Main product (center, large)
   - Side products (left/right, smaller)
   - Text overlay (top)
   - Price/offer (bottom)
4. Export comparison layout
```

## Performance & Cost

### Product Image Scraper
- **Per Operation:** ~2-5 seconds
- **Cost:** < $0.001 per scrape
- **Storage:** ~$0.015 per GB/month (R2)
- **Bandwidth:** Free (R2 → Cloudflare CDN)

### Composite Service
- **Per Composite:** ~3-8 seconds
- **Cost:** ~$0.02 per composite (compute + storage)
- **Formats:** JPEG, PNG, WebP

### Dynamic Mockups
- **Per Mockup:** ~15-30 seconds
- **Cost:** $0.10 per render
- **Template Upload:** One-time, reusable

## Quality Assurance

### Image Quality Scoring
```python
def calculate_quality_score(image):
    score = 0

    # Resolution (0-30 points)
    pixels = width * height
    if pixels >= 1_000_000:  # 1MP+
        score += 30
    elif pixels >= 500_000:
        score += 25
    elif pixels >= 250_000:
        score += 20

    # Aspect ratio (0-20 points)
    ratio = width / height
    if 0.8 <= ratio <= 1.2:  # Square/portrait
        score += 20
    elif 0.5 <= ratio <= 2.0:
        score += 15

    # File size (0-15 points)
    if 50KB <= file_size <= 2MB:  # Sweet spot
        score += 15
    elif 10KB <= file_size <= 5MB:
        score += 10

    # Product indicators (0-20 points)
    keywords = ['product', 'bottle', 'box', 'package', 'hero']
    if any(k in url.lower() or k in alt_text.lower() for k in keywords):
        score += 20

    # Context/position (0-15 points)
    if 'hero' in context or 'main' in context:
        score += 15
    elif 'featured' in context:
        score += 10

    return min(score, 100.0)
```

### Image Classification
- **Hero:** Width ≥ 800px AND Height ≥ 600px AND hero/main in context
- **Product:** Keywords in URL/alt (bottle, box, package, product)
- **Lifestyle:** Keywords in URL/alt (gym, hand, person, lifestyle)

## Error Handling

### Scraper Failures
- Network errors → Retry with exponential backoff
- Invalid images → Skip and continue
- No images found → Return empty result, don't fail

### Composite Failures
- Invalid URLs → Return error with specific message
- Download errors → Retry up to 3 times
- Render errors → Log detailed error, return 500

### Storage Failures
- R2 upload errors → Retry with different region
- CDN purge errors → Log warning, continue (not critical)

## Testing

### Unit Tests
```bash
pytest tests/services/test_product_image_scraper.py
pytest tests/services/test_composite_image_service.py
```

### Integration Tests
```bash
pytest tests/integration/test_image_workflow.py
```

### End-to-End Test
```bash
# 1. Scrape images from test sales page
curl -X POST /api/intelligence/product-images/scrape \
  -d '{"campaign_id": "test", "sales_page_url": "https://example.com/product"}'

# 2. Generate AI background
curl -X POST /api/content/generate/image \
  -d '{"prompt": "modern gym", "campaign_id": "test"}'

# 3. Composite together
curl -X POST /api/content/composite/create \
  -d '{"campaign_id": "test", "background_url": "...", "foreground_layers": [...]}'
```

## Deployment Status

- ✅ Product Image Scraper service implemented
- ✅ Composite Image Service implemented
- ✅ Database migration completed (scraped_images table)
- ✅ API routes registered
- ⏳ Railway deployment in progress
- ⏳ Frontend integration pending
- ⏳ User documentation pending

## Next Steps

1. **Test with Real Sales Pages**
   - Supplement products
   - eBook pages
   - Software products
   - Physical products

2. **Frontend Integration**
   - Add "Extract Product Images" button to campaign page
   - Show gallery of scraped images
   - Add composite builder UI
   - Preview before finalizing

3. **Enhancements**
   - AI-powered image selection (computer vision)
   - Automatic background removal
   - Smart cropping to product focus
   - Batch processing for multiple products

4. **Analytics**
   - Track which images perform best
   - A/B test different compositions
   - Optimize based on conversion data

## Documentation Links

- [Product Image Scraper Guide](PRODUCT_IMAGE_SCRAPER_GUIDE.md)
- [Composite Architecture](src/content/ARCHITECTURE.md)
- [Mockup Solution](MOCKUP_SOLUTION_FINAL.md)
- [Template Priority List](MOCKUP_TEMPLATES_PRIORITY.md)

---

**Status:** ✅ Backend Complete, Ready for Testing & Frontend Integration
**Impact:** Solves AI text rendering problem, enables professional composite images
**Cost:** < $0.03 per complete workflow (scrape + composite)
**Performance:** < 15 seconds end-to-end
