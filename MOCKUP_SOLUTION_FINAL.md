# Final Mockup Solution: Custom PSD Templates + Dynamic Mockups

## Discovery: Dynamic Mockups Supports Custom Templates!

Dynamic Mockups allows **uploading custom PSD files** as templates. This solves our problem!

### API Endpoint
```
POST https://app.dynamicmockups.com/api/v1/psd/upload
Headers:
  x-api-key: YOUR_API_KEY
  Accept: application/json

Body:
{
  "psd_file_url": "https://r2.com/our-supplement-bottle.psd",
  "psd_name": "Supplement Bottle - Front View",
  "psd_category_id": 6,
  "mockup_template": {
    "create_after_upload": true,
    "collections": []
  }
}
```

## Solution: Create Our Own Templates

### Step 1: Design PSD Templates

**Product Categories We Need:**
1. Supplement Bottles (various angles)
2. Product Boxes (front, angled)
3. Book Covers (hardcover, paperback)
4. Food Packaging (bags, pouches)
5. Software Boxes
6. Labels & Stickers

**PSD Requirements:**
- **Dimensions:** 1500x1500px
- **Resolution:** 72 dpi
- **Smart Objects:** For label/design areas
- **Layer Structure:** Organized, named layers
- **File Size:** Optimized, delete cropped pixels

### Step 2: Smart Object Setup

**Example: Supplement Bottle PSD**
```
Layers:
├── Background (rasterized)
├── Bottle (rasterized)
│   ├── Highlights
│   ├── Shadows
│   └── Reflection
├── Label [SMART OBJECT] ← User design goes here
├── Cap (rasterized)
└── Shadow (rasterized)
```

**Smart Object = Design Placeholder**
- Contains only color fill layer
- User's label image replaces this
- Dynamic Mockups handles the rest

### Step 3: Upload Templates

**New Service:**
```python
# src/storage/services/custom_mockup_manager.py

class CustomMockupManager:
    """Manage custom PSD template uploads"""

    async def upload_template(
        self,
        psd_file_url: str,
        template_name: str,
        category: str,
        description: str
    ):
        """Upload custom PSD to Dynamic Mockups"""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://app.dynamicmockups.com/api/v1/psd/upload",
                headers={
                    "x-api-key": self.api_key,
                    "Accept": "application/json"
                },
                json={
                    "psd_file_url": psd_file_url,
                    "psd_name": template_name,
                    "psd_category_id": self._get_category_id(category),
                    "mockup_template": {
                        "create_after_upload": True
                    }
                }
            ) as response:
                return await response.json()
```

### Step 4: Use Like Any Template

Once uploaded, custom templates work identically to built-in ones:

```python
# Generate mockup using our custom bottle template
await dynamic_mockups_service.generate_mockup(
    image_url="https://r2.com/user-label-design.png",
    mockup_uuid="our-custom-bottle-uuid",  # From upload response
    smart_object_uuid="label-layer-uuid"
)
```

## Hybrid Solution: Best of Both Worlds

### Dynamic Mockups Custom Templates
**For:** Supplement bottles, product boxes, books, packaging
**How:** We design and upload PSD templates
**Why:** 3D realism, consistent quality, swap labels easily

### Flux AI Text Generation
**For:** When text needs to be part of the image (not a separate layer)
**How:** Direct AI generation with text prompts
**Why:** Perfect text rendering, no Photoshop needed

### Our Composite System
**For:** Final assembly with backgrounds and additional elements
**How:** Combine mockup + scene + text overlays
**Why:** Complete marketing visuals

## Implementation Plan

### Phase 1: Template Design (External Designer or AI)

**Option A: Hire Photoshop Designer**
- Cost: $50-200 per template
- Quality: Professional, perfect smart objects
- Time: 1-3 days per template

**Option B: AI-Generated Base + Manual Smart Objects**
- Use Flux/Midjourney to generate photorealistic product
- Add smart object layers in Photoshop
- Cost: ~$10 in AI + 1 hour work
- Time: Few hours per template

**Initial Templates Needed:**
1. Supplement Bottle - Front View
2. Supplement Bottle - Angled View
3. Product Box - Front
4. Product Box - 3D Angled
5. Book Cover - Hardcover
6. Supplement Bottle - Lifestyle (hand holding)

### Phase 2: Upload System

```python
# src/storage/services/custom_mockup_manager.py

CUSTOM_TEMPLATES = [
    {
        "name": "Supplement Bottle - Front View",
        "psd_path": "templates/supplement-bottle-front.psd",
        "category": "supplement",
        "description": "Professional supplement bottle, front facing",
        "smart_objects": [
            {"name": "Front Label", "layer": "Label"}
        ]
    },
    {
        "name": "Product Box - 3D Angled",
        "psd_path": "templates/product-box-angled.psd",
        "category": "packaging",
        "description": "Product box with three visible sides",
        "smart_objects": [
            {"name": "Front Panel", "layer": "Front"},
            {"name": "Side Panel", "layer": "Side"},
            {"name": "Top Panel", "layer": "Top"}
        ]
    }
]

async def initialize_templates():
    """Upload all custom templates on startup"""
    manager = CustomMockupManager()

    for template in CUSTOM_TEMPLATES:
        # Upload PSD to R2
        psd_url = await upload_to_r2(template["psd_path"])

        # Upload to Dynamic Mockups
        result = await manager.upload_template(
            psd_file_url=psd_url,
            template_name=template["name"],
            category=template["category"],
            description=template["description"]
        )

        # Store mockup UUID for later use
        await save_template_mapping(
            category=template["category"],
            name=template["name"],
            mockup_uuid=result["mockup_uuid"]
        )
```

### Phase 3: Template Categories

Update category detection to use our custom templates:

```python
# src/storage/services/dynamic_mockups_service.py

async def get_available_mockups(self, category: Optional[str] = None):
    """Get templates including our custom uploads"""

    # Fetch from API (includes our uploads)
    api_templates = await self._fetch_from_api()

    # Add our custom templates metadata
    custom_templates = await self._get_custom_templates(category)

    return api_templates + custom_templates
```

### Phase 4: Template Library Database

```sql
CREATE TABLE custom_mockup_templates (
    id UUID PRIMARY KEY,
    template_name VARCHAR(255),
    category VARCHAR(100),
    psd_r2_path TEXT,
    mockup_uuid VARCHAR(255),  -- From Dynamic Mockups
    smart_objects JSONB,
    preview_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Example data
INSERT INTO custom_mockup_templates VALUES (
    uuid_generate_v4(),
    'Supplement Bottle - Front View',
    'supplement',
    'mockup-templates/supplement-bottle-front.psd',
    'abc-123-mockup-uuid',
    '[{"name": "Front Label", "uuid": "label-uuid"}]',
    'https://r2.com/previews/supplement-bottle.jpg',
    true,
    NOW(),
    NOW()
);
```

## Cost Analysis

### Template Creation (One-Time)
- **Photoshop Designer:** $50-200/template × 10 templates = $500-2000
- **AI + Manual Setup:** $10/template × 10 templates = $100
- **Recommendation:** Start with AI + manual for MVP

### Ongoing Usage
- **Mockup Generation:** $0.10 per render (Dynamic Mockups)
- **Storage:** ~$0.01 per PSD (R2)
- **Total:** ~$0.11 per mockup

### Comparison
| Solution | Setup Cost | Per Mockup | Quality | Flexibility |
|----------|-----------|------------|---------|-------------|
| **Custom PSD Templates** | $100-2000 | $0.10 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Flux AI Only** | $0 | $0.05 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Stock Templates (Wrong Category)** | $0 | $0.10 | ⭐⭐ | ⭐ |

## Recommended Final Solution

### Primary: Custom PSD Templates
- Upload 10-15 core product templates
- Use Dynamic Mockups for rendering
- Professional quality, consistent results

### Fallback: Flux AI
- For unique products not in template library
- For text-heavy designs (book covers)
- Faster iteration during design phase

### Assembly: Our Composite System
- Combine mockups with AI backgrounds
- Add text overlays and CTAs
- Final marketing-ready images

## Timeline

### Week 1: Template Creation
- Design 6 core templates (bottles, boxes, books)
- Test smart object setup
- Upload to Dynamic Mockups

### Week 2: Integration
- Implement custom_mockup_manager.py
- Update template fetching logic
- Test full workflow

### Week 3: Polish
- Add remaining templates
- Build template selector UI
- Documentation and testing

## User Experience

### Final Workflow

**Step 1: Design Label/Cover**
- User creates label design (or AI generates it)
- Upload to platform

**Step 2: Select Template**
```
Categories:
├── Supplement Bottles ✓ (our custom templates)
│   ├── Front View
│   ├── Angled View
│   └── Lifestyle (hand holding)
├── Product Boxes ✓ (our custom templates)
│   ├── Front View
│   ├── 3D Angled
│   └── Flat Lay
├── Books ✓ (our custom templates)
│   ├── Hardcover
│   └── Paperback
└── Apparel (Dynamic Mockups built-in)
    ├── T-shirts
    └── Hoodies
```

**Step 3: Generate Mockup**
- System applies design to template
- Renders in ~5 seconds
- Returns photorealistic mockup

**Step 4: Composite (Optional)**
- Place mockup on AI-generated scene
- Add product name text
- Add CTA button
- Export final marketing image

## Conclusion

✅ **Problem Solved:** Custom PSD uploads give us unlimited product types

✅ **Quality Maintained:** Professional 3D mockups, not just flat AI

✅ **Cost Effective:** One-time template creation, low per-use cost

✅ **Modular:** Doesn't break existing systems

✅ **Scalable:** Add new templates anytime

**Next Action:** Create first 3 templates (bottle, box, book) to validate approach

---

**Status:** Ready to implement
**Blocker:** Need PSD templates created
**Decision:** Start with AI-generated base + manual smart objects ($100 budget)
