# CampaignForge Mockup System - Implementation Plan

## Final Solution: Envato Templates + Dynamic Mockups API + Composite System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Template Sources                                   │
│                                                              │
│  Envato Elements          Dynamic Mockups        Flux AI    │
│  (Download PSD)    →    (Generate Mockups)   (Text in Images)│
│  $16.50/month           $0.10 per render      $0.05 per gen  │
└─────────────────────────────────────────────────────────────┘
                              ↓ URLs
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: Composite System (✅ Already Built)                │
│                                                              │
│  composite_image_service.py - Combines layers               │
│  - Mockup + AI Background + Text Overlays                   │
│  - Smart positioning, effects, final assembly               │
└─────────────────────────────────────────────────────────────┘
                              ↓ Final Image
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: Storage & Delivery                                 │
│                                                              │
│  R2 Storage → Cloudflare CDN → User                         │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Phase 1: Template Acquisition (Week 1)

**Action Items:**

1. **Get Envato Elements Subscription**
   - URL: https://elements.envato.com/pricing
   - Cost: $16.50/month (annual plan)
   - Cancel after 1 month if needed (keep downloaded templates)

2. **Download Initial Template Set**

   **Priority Templates:**
   - [ ] Supplement Bottle - Front View (3-4 variations)
   - [ ] Supplement Bottle - Angled View (2-3 variations)
   - [ ] Supplement Bottle - Hand Holding (lifestyle)
   - [ ] Product Box - Front View
   - [ ] Product Box - 3D Angled View
   - [ ] Book Cover - Hardcover
   - [ ] Book Cover - Paperback
   - [ ] Food Packaging - Pouch/Bag

   **Search Terms:**
   - "supplement bottle mockup psd"
   - "product box mockup psd"
   - "book cover mockup psd"
   - "packaging mockup psd smart object"

3. **Quality Checklist**
   - ✅ Smart objects present
   - ✅ High resolution (1500x1500px minimum)
   - ✅ Clean layer structure
   - ✅ Professional appearance
   - ✅ Multiple angles/views

### Phase 2: Template Preparation (Week 1-2)

**Verify PSD Requirements:**

```
Required Format:
├── Dimensions: 1500x1500px or larger
├── Resolution: 72 dpi
├── Smart Objects: For label/design areas
├── Layer Structure:
│   ├── Background (rasterized)
│   ├── Product Elements (rasterized)
│   ├── Smart Object (design placeholder)
│   └── Effects/Shadows (rasterized)
└── File Size: Optimized, <50MB per file
```

**Preparation Steps:**

1. Open each PSD in Photoshop
2. Verify smart object layers work correctly
3. Test with sample design
4. Optimize file size (delete cropped pixels)
5. Upload to R2 storage
6. Document smart object layer names

### Phase 3: Upload System Implementation (Week 2)

**Create Custom Template Manager:**

```python
# src/storage/services/custom_mockup_manager.py

"""
Custom Mockup Template Manager
Uploads PSD templates to Dynamic Mockups and tracks them
"""

from typing import Dict, List, Optional, Any
import aiohttp
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TemplateMetadata:
    """Metadata for custom template"""
    name: str
    category: str
    psd_r2_path: str
    description: str
    smart_objects: List[Dict[str, str]]
    preview_image_url: Optional[str] = None


class CustomMockupManager:
    """Manage custom PSD template uploads to Dynamic Mockups"""

    def __init__(self):
        self.api_key = os.getenv("DYNAMIC_MOCKUPS_API_KEY")
        self.api_url = "https://app.dynamicmockups.com/api/v1"

    async def upload_template(
        self,
        psd_url: str,
        template_name: str,
        category: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Upload PSD to Dynamic Mockups

        Args:
            psd_url: Public URL of PSD file (from R2)
            template_name: Display name for template
            category: Template category (supplement, packaging, etc.)
            description: Template description

        Returns:
            Dict with mockup_uuid and smart_object info
        """

        try:
            logger.info(f"📤 Uploading template: {template_name}")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/psd/upload",
                    headers={
                        "x-api-key": self.api_key,
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    json={
                        "psd_file_url": psd_url,
                        "psd_name": template_name,
                        "psd_category_id": self._get_category_id(category),
                        "mockup_template": {
                            "create_after_upload": True
                        }
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Upload failed: {error_text}")
                        return {
                            "success": False,
                            "error": error_text
                        }

                    result = await response.json()
                    logger.info(f"✅ Template uploaded: {result.get('mockup_uuid')}")

                    return {
                        "success": True,
                        "mockup_uuid": result.get("mockup_uuid"),
                        "template_name": template_name,
                        "smart_objects": result.get("smart_objects", []),
                        "thumbnail": result.get("thumbnail")
                    }

        except Exception as e:
            logger.error(f"Template upload error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_category_id(self, category: str) -> int:
        """Map our categories to Dynamic Mockups category IDs"""
        category_map = {
            "supplement": 6,      # Other (custom category)
            "packaging": 6,
            "book": 6,
            "apparel": 1,         # T-shirts (built-in)
            "drinkware": 4,       # Mugs (built-in)
        }
        return category_map.get(category, 6)

    async def get_uploaded_templates(self) -> List[Dict[str, Any]]:
        """Get list of all uploaded custom templates"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/mockups",
                    headers={
                        "x-api-key": self.api_key,
                        "Accept": "application/json"
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", [])
                    return []

        except Exception as e:
            logger.error(f"Error fetching templates: {e}")
            return []


# Initial template definitions
INITIAL_TEMPLATES = [
    TemplateMetadata(
        name="Supplement Bottle - Front View",
        category="supplement",
        psd_r2_path="mockup-templates/supplement-bottle-front.psd",
        description="Professional supplement bottle, front facing label view",
        smart_objects=[
            {"name": "Front Label", "layer": "Label"}
        ]
    ),
    TemplateMetadata(
        name="Supplement Bottle - Angled View",
        category="supplement",
        psd_r2_path="mockup-templates/supplement-bottle-angled.psd",
        description="Supplement bottle at 45 degree angle showing depth",
        smart_objects=[
            {"name": "Front Label", "layer": "Label"}
        ]
    ),
    TemplateMetadata(
        name="Product Box - 3D View",
        category="packaging",
        psd_r2_path="mockup-templates/product-box-3d.psd",
        description="Product box with three visible sides",
        smart_objects=[
            {"name": "Front Panel", "layer": "Front"},
            {"name": "Side Panel", "layer": "Side"},
            {"name": "Top Panel", "layer": "Top"}
        ]
    ),
    TemplateMetadata(
        name="Book Cover - Hardcover",
        category="book",
        psd_r2_path="mockup-templates/book-hardcover.psd",
        description="Hardcover book with visible spine",
        smart_objects=[
            {"name": "Front Cover", "layer": "Cover"},
            {"name": "Spine", "layer": "Spine"}
        ]
    ),
]


async def initialize_custom_templates():
    """
    Initialize custom templates on startup
    Call this once to upload all Envato templates
    """

    manager = CustomMockupManager()
    r2_service = get_r2_service()

    results = []

    for template in INITIAL_TEMPLATES:
        try:
            # Get PSD URL from R2
            psd_url = f"https://r2.campaignforge.com/{template.psd_r2_path}"

            # Upload to Dynamic Mockups
            result = await manager.upload_template(
                psd_url=psd_url,
                template_name=template.name,
                category=template.category,
                description=template.description
            )

            if result["success"]:
                # Store in database for future reference
                await save_template_mapping(
                    template_name=template.name,
                    category=template.category,
                    mockup_uuid=result["mockup_uuid"],
                    smart_objects=result["smart_objects"]
                )

            results.append(result)

        except Exception as e:
            logger.error(f"Failed to initialize template {template.name}: {e}")
            results.append({
                "success": False,
                "template": template.name,
                "error": str(e)
            })

    return results
```

### Phase 4: Database Schema (Week 2)

**Create Template Tracking Table:**

```sql
-- Alembic migration: 004_add_custom_mockup_templates.py

CREATE TABLE custom_mockup_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,

    -- Storage
    psd_r2_path TEXT NOT NULL,
    preview_url TEXT,

    -- Dynamic Mockups Integration
    mockup_uuid VARCHAR(255) UNIQUE NOT NULL,
    smart_objects JSONB NOT NULL DEFAULT '[]',

    -- Metadata
    source VARCHAR(50) DEFAULT 'envato',  -- envato, custom, ai-generated
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    INDEX idx_category (category),
    INDEX idx_mockup_uuid (mockup_uuid),
    INDEX idx_active (is_active)
);

-- Example data
INSERT INTO custom_mockup_templates
(template_name, category, description, psd_r2_path, mockup_uuid, smart_objects, source)
VALUES
(
    'Supplement Bottle - Front View',
    'supplement',
    'Professional supplement bottle, front facing label view',
    'mockup-templates/supplement-bottle-front.psd',
    'PLACEHOLDER_UUID',  -- Will be filled after upload
    '[{"uuid": "label-uuid", "name": "Front Label", "layer": "Label"}]',
    'envato'
);
```

### Phase 5: API Integration (Week 3)

**Update Mockup Routes:**

```python
# src/content/api/mockup_routes.py

from src.storage.services.custom_mockup_manager import CustomMockupManager

@router.post("/upload-custom-template")
async def upload_custom_template(
    psd_file: UploadFile = File(...),
    template_name: str = Form(...),
    category: str = Form(...),
    description: str = Form(None),
    current_user: dict = Depends(require_admin)  # Admin only
):
    """
    Upload custom PSD template

    **Admin Only** - Upload Envato PSDs or custom designs
    """

    try:
        # Upload PSD to R2
        r2_service = get_r2_service()
        psd_data = await psd_file.read()
        psd_key = f"mockup-templates/{template_name.lower().replace(' ', '-')}.psd"

        r2_result = await r2_service.upload_file(
            file_data=psd_data,
            key=psd_key,
            content_type="application/x-photoshop"
        )

        if not r2_result.get("success"):
            raise HTTPException(status_code=500, detail="R2 upload failed")

        # Upload to Dynamic Mockups
        manager = CustomMockupManager()
        dm_result = await manager.upload_template(
            psd_url=r2_result["url"],
            template_name=template_name,
            category=category,
            description=description
        )

        if not dm_result["success"]:
            raise HTTPException(status_code=500, detail="Dynamic Mockups upload failed")

        # Save to database
        # ... (database insert code)

        return {
            "success": True,
            "template_name": template_name,
            "mockup_uuid": dm_result["mockup_uuid"],
            "smart_objects": dm_result["smart_objects"]
        }

    except Exception as e:
        logger.error(f"Template upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/custom")
async def get_custom_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of custom uploaded templates"""

    # Query database
    query = "SELECT * FROM custom_mockup_templates WHERE is_active = true"
    if category:
        query += f" AND category = '{category}'"

    # ... (execute query)

    return {
        "success": True,
        "templates": templates,
        "count": len(templates)
    }
```

### Phase 6: Frontend Updates (Week 3-4)

**Update Template Selector:**

```typescript
// src/components/mockups/MockupTemplateSelector.tsx

// Add custom templates section
const [customTemplates, setCustomTemplates] = useState<Template[]>([]);

useEffect(() => {
  async function loadTemplates() {
    // Load built-in Dynamic Mockups templates
    const builtIn = await api.get('/api/content/mockups/templates');

    // Load custom uploaded templates
    const custom = await api.get('/api/content/mockups/templates/custom');

    // Merge and categorize
    setTemplates([...builtIn.templates, ...custom.templates]);
  }

  loadTemplates();
}, []);

// Display with badges
{templates.map(template => (
  <TemplateCard key={template.uuid}>
    <Badge>{template.source === 'envato' ? '⭐ Premium' : 'Built-in'}</Badge>
    <TemplatePreview src={template.preview_url} />
    <TemplateName>{template.name}</TemplateName>
  </TemplateCard>
))}
```

## Cost Breakdown

### One-Time Setup
- Envato Elements: $16.50 (1 month to download templates)
- Development time: Already done ✅
- **Total: $16.50**

### Per-Use Costs
- Mockup generation: $0.10 (Dynamic Mockups)
- Background scene: $0.04 (DALL-E 3)
- Composite assembly: $0.02 (our service)
- **Total per final image: $0.16**

### Monthly Ongoing
- R2 Storage: ~$1-5 for PSD files
- API calls: Pay-as-you-go
- **Total: ~$5-10/month**

## Testing Plan

### Unit Tests
```python
# tests/test_custom_mockup_manager.py

async def test_upload_template():
    manager = CustomMockupManager()
    result = await manager.upload_template(
        psd_url="https://r2.test.com/test.psd",
        template_name="Test Template",
        category="supplement",
        description="Test description"
    )
    assert result["success"] == True
    assert "mockup_uuid" in result

async def test_get_uploaded_templates():
    manager = CustomMockupManager()
    templates = await manager.get_uploaded_templates()
    assert isinstance(templates, list)
```

### Integration Tests
1. Upload sample PSD to R2
2. Call upload_template API
3. Verify template appears in Dynamic Mockups dashboard
4. Generate mockup with test design
5. Verify output quality

## Rollout Timeline

### Week 1: Template Acquisition
- [ ] Day 1: Get Envato subscription
- [ ] Day 2-3: Download 10-15 high-quality templates
- [ ] Day 4-5: Prepare and optimize PSDs

### Week 2: Backend Implementation
- [ ] Day 1: Create custom_mockup_manager.py
- [ ] Day 2: Database migration
- [ ] Day 3: API routes
- [ ] Day 4-5: Testing and bug fixes

### Week 3: Frontend Integration
- [ ] Day 1-2: Update template selector UI
- [ ] Day 3: Admin upload interface
- [ ] Day 4-5: End-to-end testing

### Week 4: Launch
- [ ] Day 1: Upload all templates to production
- [ ] Day 2: User testing
- [ ] Day 3: Documentation
- [ ] Day 4-5: Monitor and optimize

## Success Metrics

- ✅ 10+ custom templates uploaded
- ✅ <5 second mockup generation time
- ✅ >95% successful renders
- ✅ User satisfaction with template quality
- ✅ No impact on existing systems

## Documentation Links

- Architecture: `/src/content/ARCHITECTURE.md`
- Composite System: `/COMPOSITE_SYSTEM_SUMMARY.md`
- Mockup Solution: `/MOCKUP_SOLUTION_FINAL.md`
- This Plan: `/IMPLEMENTATION_PLAN.md`

---

**Status:** Ready to implement
**Next Action:** Get Envato Elements subscription
**Estimated Completion:** 3-4 weeks
**Owner:** Development Team
