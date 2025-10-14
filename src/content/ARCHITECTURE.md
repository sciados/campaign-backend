# Content Generation Architecture

## Modular Design Principles

This document outlines the modular architecture for content generation to ensure changes to one system don't break others.

## Current Modules (Isolated)

### 1. **Image Generation** (`src/content/generators/image_generator.py`)
- **Purpose**: Generate standalone AI images from prompts
- **Providers**: DALL-E 3, Stable Diffusion, Midjourney
- **Output**: Single image URL
- **Dependencies**: None (standalone)
- **Used by**: Content generation, variations, platform images

### 2. **Image Variations** (`src/content/generators/image_variation_service.py`)
- **Purpose**: Create variations of existing images
- **Providers**: DALL-E 2 (variations API)
- **Output**: Multiple variation URLs
- **Dependencies**: Requires existing image
- **Used by**: A/B testing, alternative versions

### 3. **Platform Images** (`src/content/generators/enhanced_platform_image_generator.py`)
- **Purpose**: Generate images optimized for specific platforms
- **Providers**: DALL-E 3, Stable Diffusion
- **Output**: Platform-specific dimensions and formats
- **Dependencies**: Image generation module
- **Used by**: Social media content creation

### 4. **Dynamic Mockups** (`src/storage/services/dynamic_mockups_service.py`)
- **Purpose**: Apply images to professional product mockup templates
- **Provider**: Dynamic Mockups API
- **Output**: Photo-realistic product mockup
- **Dependencies**: Requires input image (label/design)
- **Used by**: Product visualization

### 5. **Video Generation** (`src/content/services/video_generation_service.py`)
- **Purpose**: Create video content from scripts and scenes
- **Providers**: Multiple (Haiper, Runway, Luma, etc.)
- **Output**: Video file
- **Dependencies**: AI image generator for scene backgrounds
- **Used by**: Video campaigns

## New Module: **Composite Image System**

### Purpose
Combine multiple image assets into a single composite:
- Background scenes (AI-generated or stock)
- Product mockups (from Dynamic Mockups)
- Text overlays (product names, CTAs)
- Additional elements (logos, badges)

### Design Requirements

#### Modularity
- **Independent of existing modules**: Doesn't modify image generation or mockup generation
- **Consumes outputs**: Takes URLs from other modules as inputs
- **Stateless**: Each composite is independent
- **Reversible**: Can extract layers from composite metadata

#### API Contract
```python
class CompositeImageRequest:
    background_image_url: str          # From AI image generator or stock
    foreground_layers: List[Layer]     # Product mockups, logos, etc.
    text_layers: List[TextLayer]       # Product names, CTAs, etc.
    composition_rules: CompositionRules # Positioning, scaling, blending

class Layer:
    image_url: str
    position: Position                  # x, y coordinates or anchors
    scale: float                        # Resize factor
    opacity: float                      # Transparency
    blend_mode: str                     # normal, multiply, overlay, etc.
    z_index: int                        # Layer order

class TextLayer:
    text: str
    font_family: str
    font_size: int
    color: str
    position: Position
    alignment: str
    stroke: Optional[Stroke]
    shadow: Optional[Shadow]
```

### Service Architecture

```
src/content/services/
├── composite_image_service.py      # Main compositor
├── image_composition_rules.py      # Smart positioning logic
└── text_rendering_service.py       # Text overlay rendering

src/content/api/
└── composite_routes.py             # API endpoints
```

### Workflow Examples

#### Example 1: Mockup on AI Background
```
1. User generates AI background scene
   → ai_image_generator.py → background_url

2. User generates product mockup
   → dynamic_mockups_service.py → mockup_url

3. User creates composite
   → composite_image_service.py
   Input: background_url, mockup_url, text_layers
   Output: composite_url
```

#### Example 2: Platform Image with Mockup
```
1. User generates platform-specific background
   → enhanced_platform_image_generator.py → platform_bg_url

2. User applies label to mockup template
   → dynamic_mockups_service.py → mockup_url

3. User adds text and composes
   → composite_image_service.py
   Input: platform_bg_url, mockup_url, text="New Product!", cta="Buy Now"
   Output: final_platform_image_url
```

## Isolation Strategy

### How Changes Won't Break Other Modules

1. **Separate API Routes**: New `/api/content/composite` endpoints
2. **No Shared State**: Each module has its own service class
3. **Interface-Based**: Modules communicate via URLs, not objects
4. **Backward Compatible**: Existing endpoints unchanged
5. **Feature Flags**: Can disable composite system without affecting others
6. **Independent Testing**: Each module has its own test suite

### Database Isolation

```sql
-- New table for composites (doesn't touch existing tables)
CREATE TABLE composite_images (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    user_id UUID REFERENCES users(id),
    background_layer JSONB,      -- {url, source_module}
    foreground_layers JSONB[],   -- [{url, position, scale, ...}]
    text_layers JSONB[],         -- [{text, font, position, ...}]
    final_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP
);

-- Doesn't modify:
-- - generated_content (existing image storage)
-- - campaigns (unchanged)
-- - intelligence_analysis (unchanged)
```

## Migration Path

### Phase 1: Basic Compositor (This PR)
- Create composite_image_service.py
- Add basic layer composition (background + foreground)
- Simple text overlay support
- New API endpoint: POST /api/content/composite/create

### Phase 2: Advanced Features (Future)
- Smart positioning based on intelligence
- Template presets (lifestyle, gym, office)
- Batch compositing for A/B testing
- Advanced blending modes

### Phase 3: UI Integration (Future)
- Visual composer in frontend
- Drag-and-drop layer positioning
- Real-time preview
- Template library

## Testing Strategy

```python
# Test isolation - mock other services
@pytest.fixture
def mock_image_urls():
    return {
        "background": "https://r2.example.com/bg.jpg",
        "mockup": "https://r2.example.com/mockup.png"
    }

def test_composite_doesnt_call_image_generator(mock_image_urls):
    # Composite should only use URLs, not trigger new generation
    compositor = CompositeImageService()
    result = compositor.create_composite(
        background_url=mock_image_urls["background"],
        mockup_url=mock_image_urls["mockup"]
    )
    assert result.success
    # Verify no calls to image_generator

def test_existing_image_generation_unaffected():
    # Existing image generation should work without composite service
    generator = ImageGenerator()
    result = generator.generate(prompt="test")
    assert result.success
```

## Monitoring

Track usage independently:
- `composite_images_created` counter
- `composite_generation_time` histogram
- `composite_errors` counter

Separate from:
- `images_generated` (existing)
- `mockups_generated` (existing)
- `variations_created` (existing)

## Rollback Strategy

If composite system has issues:
1. Disable route: Remove from router
2. Flag check: Add `ENABLE_COMPOSITE_IMAGES=false`
3. Old workflows continue working
4. No data loss (composites in separate table)

---

**Last Updated**: 2025-01-14
**Owner**: Content Generation Team
**Status**: Design Phase
