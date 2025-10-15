# Mockup & Text Rendering Solution Strategy

## The Problem

**Dynamic Mockups categories don't match our needs:**
- ❌ They have: T-shirts, mugs, phone cases, tote bags, picture frames
- ✅ We need: Supplement bottles, product boxes, book covers, food packaging

**Additionally:** We need accurate text rendering for:
- Product labels on bottles
- Book covers with titles
- Packaging with brand names
- Marketing materials with CTAs

## Research Findings (January 2025)

### Best AI Text Rendering: Flux by Black Forest Labs

**Flux excels at text rendering** - gets words right nearly every time
- Better than DALL-E 3, Midjourney, and Stable Diffusion for text
- Perfect for logos, labels, product names
- Text looks clear and natural in images

**Official API:** https://docs.bfl.ml
- Endpoint: `https://api.bfl.ai/v1/flux-pro-1.1`
- Auth: `x-key` header
- Models: flux-pro, flux-dev, flux-kontext

### Product Mockup Alternatives

**Web-Based (No Public API):**
1. **Mockey.ai** - 1000+ bottle/supplement mockups (FREE)
2. **Packify.ai** - 18,000+ mockup templates
3. **ArtificialStudio.ai** - Bottles, jars, boxes ($0.0075/mockup)
4. **Pixelcut.ai** - 3D product packaging

**Problem:** None have public APIs documented

## Recommended Solution: Hybrid Approach

### Strategy 1: Flux + Our Composite System (RECOMMENDED)

**Workflow:**
1. Generate product with text using **Flux AI**
   - Prompt: "Photorealistic supplement bottle, white label with 'PRO FUEL' in bold black text, modern minimalist design"
   - Flux renders text accurately in one generation
   - Output: Complete product with label

2. Generate background scene (existing system)
   - Prompt: "Modern gym interior with natural lighting"
   - Use existing image_generator.py

3. Composite them together (new system)
   - Use composite_image_service.py
   - Position product on background
   - Add additional text (CTA, badge)

**Advantages:**
✅ Single AI generation creates product with text
✅ No separate mockup service needed
✅ Modular: Uses existing composite system
✅ Cost-effective: ~$0.05 per image
✅ Full control over text appearance
✅ API available NOW

**Disadvantages:**
⚠️ Not true "3D mockup" (but photorealistic)
⚠️ Can't swap labels after generation

### Strategy 2: Keep Dynamic Mockups for Apparel + Add Flux for Products

**Implementation:**
- Dynamic Mockups → T-shirts, mugs, tote bags
- Flux → Bottles, boxes, books, packaging

**Database:**
```python
MOCKUP_PROVIDERS = {
    "apparel": "dynamic_mockups",      # T-shirts, hoodies
    "drinkware": "dynamic_mockups",    # Mugs, tumblers
    "accessories": "dynamic_mockups",  # Phone cases, tote bags
    "supplements": "flux",             # Bottles, jars
    "books": "flux",                   # Book covers
    "packaging": "flux",               # Boxes, bags, labels
}
```

**Advantages:**
✅ Best tool for each category
✅ Dynamic Mockups great for what it does
✅ Flux covers the gaps

**Disadvantages:**
⚠️ Two different workflows
⚠️ More complex to maintain

### Strategy 3: Full Flux Text-to-Image Solution

**Replace mockup system entirely with Flux:**

**Prompt Engineering:**
```
"Professional product photography, [PRODUCT_TYPE],
 [LABEL_TEXT] prominently displayed,
 [STYLE] design, [LIGHTING],
 placed on [BACKGROUND],
 high resolution, commercial quality"
```

**Examples:**
- "Professional product photography, white supplement bottle, 'PRO FUEL' in bold sans-serif text on clean label, modern minimalist design, studio lighting, gym background with dumbbells, high resolution"
- "Professional product photography, hardcover book, 'Marketing Mastery' title in gold embossed text, dark blue cover, elegant typography, desk setting with coffee cup, high resolution"

**Advantages:**
✅ One system for everything
✅ Unlimited product types
✅ Perfect text rendering
✅ Fastest to implement
✅ Most flexible

**Disadvantages:**
⚠️ Not traditional "mockup templates"
⚠️ Each generation is unique (no consistency)
⚠️ Can't change label after generation

## Implementation Recommendation

### Phase 1: Add Flux Service (Immediate)

Create parallel service alongside Dynamic Mockups:

```
src/storage/services/
├── dynamic_mockups_service.py    (keep for apparel)
└── flux_mockup_service.py        (NEW - for products with text)
```

**New Service Features:**
- Text-aware prompting
- Product-specific templates
- Background integration
- Consistent styling

### Phase 2: Smart Router (Next)

Create intelligent routing based on product category:

```python
# src/content/services/mockup_router.py

async def generate_mockup(
    product_type: str,
    label_text: str,
    background_style: str
):
    """Route to best mockup provider"""

    if product_type in ["tshirt", "hoodie", "mug", "tote"]:
        return await dynamic_mockups_service.generate(...)

    elif product_type in ["bottle", "jar", "box", "book"]:
        return await flux_mockup_service.generate(...)

    else:
        # Default to Flux for new product types
        return await flux_mockup_service.generate(...)
```

### Phase 3: Template Library (Future)

Build prompt templates for consistent results:

```python
PRODUCT_TEMPLATES = {
    "supplement_bottle": {
        "base_prompt": "Professional product photography, white cylindrical supplement bottle, {label_text} prominently displayed on clean label, modern minimalist design, studio lighting",
        "variations": ["front view", "angled view", "with cap off"],
        "backgrounds": ["gym", "kitchen counter", "white studio"]
    },
    "book_cover": {
        "base_prompt": "Professional product photography, hardcover book, '{title}' in elegant typography, {style} design, natural lighting",
        "variations": ["flat lay", "standing", "slightly open"],
        "backgrounds": ["wooden desk", "bookshelf", "white background"]
    }
}
```

## Cost Comparison

### Current (Dynamic Mockups)
- Apparel mockups: $0.10 each
- Product mockups: ❌ Not available

### Proposed (Flux + Dynamic Mockups)
- Apparel mockups: $0.10 (Dynamic Mockups)
- Product mockups: ~$0.05 (Flux Pro)
- Background scenes: ~$0.04 (DALL-E 3)
- Composite: $0.02 (our service)
- **Total per final image: ~$0.11-0.21**

### Alternative (Flux Only)
- Single generation with text: ~$0.05
- No separate mockup needed
- **Total: $0.05 per image**

## Technical Implementation

### New Flux Service (Minimal Code)

```python
# src/storage/services/flux_mockup_service.py

class FluxMockupService:
    """Generate product mockups with text using Flux AI"""

    def __init__(self):
        self.api_key = os.getenv("BFL_API_KEY")
        self.api_url = "https://api.bfl.ai/v1"

    async def generate_product_mockup(
        self,
        product_type: str,
        label_text: str,
        style: str = "modern minimalist",
        background: str = "white studio"
    ):
        """Generate product with accurate text rendering"""

        # Build intelligent prompt
        prompt = self._build_prompt(product_type, label_text, style, background)

        # Call Flux API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/flux-pro-1.1",
                headers={
                    "x-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "aspect_ratio": "1:1",
                    "width": 1024,
                    "height": 1024
                }
            ) as response:
                result = await response.json()
                return result

    def _build_prompt(self, product_type, label_text, style, background):
        """Smart prompt construction"""

        templates = {
            "supplement_bottle": f"Professional product photography, white cylindrical supplement bottle, '{label_text}' in bold sans-serif text on clean label, {style} design, studio lighting, {background} background, high resolution, commercial quality",

            "book_cover": f"Professional product photography, hardcover book, '{label_text}' title in elegant typography on cover, {style} design, natural lighting, {background} background, high resolution",

            "product_box": f"Professional product photography, rectangular product box, '{label_text}' prominently displayed on front, {style} design, studio lighting, {background} background, high resolution"
        }

        return templates.get(product_type, templates["supplement_bottle"])
```

### Update Mockup Routes

```python
# src/content/api/mockup_routes.py

@router.post("/generate-with-text")
async def generate_mockup_with_text(
    product_type: str,
    label_text: str,
    style: str = "modern",
    background: str = "white studio",
    current_user: dict = Depends(get_current_user)
):
    """
    Generate product mockup with accurate text rendering

    Uses Flux AI for bottles, boxes, books
    Uses Dynamic Mockups for apparel, mugs
    """

    # Route to appropriate service
    if product_type in ["tshirt", "hoodie", "mug", "tote"]:
        service = get_dynamic_mockups_service()
        # Use existing image as design
    else:
        service = get_flux_mockup_service()
        result = await service.generate_product_mockup(
            product_type=product_type,
            label_text=label_text,
            style=style,
            background=background
        )

    return result
```

## User Experience

### Before (Dynamic Mockups Only)
1. User designs label image
2. User uploads to mockup template
3. ❌ No supplement bottles available
4. ❌ Text rendering poor quality

### After (Flux + Composite)
1. User enters product name: "PRO FUEL"
2. User selects style: "Bold and Modern"
3. System generates bottle with perfect text
4. Optional: Place on AI background
5. ✅ Perfect text rendering
6. ✅ Unlimited product types

## Next Steps

### Immediate (This Week)
1. ✅ Document Dynamic Mockups limitations
2. ✅ Research alternatives
3. ⏳ Get Flux API key
4. ⏳ Implement flux_mockup_service.py
5. ⏳ Add /generate-with-text endpoint
6. ⏳ Test text rendering quality

### Short Term (Next Week)
- Build product template library
- Create smart routing system
- Add Flux examples to docs
- Update frontend UI

### Long Term (Next Month)
- A/B test Flux vs traditional mockups
- Optimize prompt engineering
- Build consistency system
- Template marketplace

## Conclusion

**Recommendation: Hybrid Approach (Strategy 2)**

- Keep Dynamic Mockups for apparel ✅
- Add Flux for products with text ✅
- Use our composite system for final assembly ✅
- Most flexible, best quality per category ✅

**Alternative: Full Flux (Strategy 3)**
- Simpler to implement
- Lower cost
- Requires testing prompt consistency

**Do NOT:** Keep Dynamic Mockups as sole provider
- Wrong product categories
- Poor text rendering
- Doesn't meet requirements

---

**Decision Point:** Get Flux API key and test before committing
**Test:** Generate supplement bottle with "PRO FUEL" text
**Compare:** Quality vs Dynamic Mockups apparel templates
**Choose:** Based on real results

**Status:** Awaiting API key and testing
**Priority:** HIGH - Blocks supplement mockup feature
