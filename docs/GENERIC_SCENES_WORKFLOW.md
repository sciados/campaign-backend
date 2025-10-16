# Generic Reusable Scenes + Mockup Workflow

## Strategic Approach

Instead of generating product-specific images, we now generate **generic, reusable background scenes** that can be used with ANY product via professional mockups.

## Why This Approach?

### Cost Efficiency
- Generate ONE scene → Use for THOUSANDS of products
- No regeneration costs per product variation
- Saves ~$0.05-0.10 per image by reusing scenes

### Scalability
- Works across ALL categories: Health, Make Money, Self-Help, Business, etc.
- One lifestyle scene works for supplements, courses, coaching, software
- Build a library of premium scenes that serve entire platform

### Quality & Speed
- Professional mockup overlays look MORE realistic than AI-generated products
- No gibberish text issues (handled by mockups)
- Faster workflow: Pick scene → Add mockup (~1-2 seconds total)

### Reusability
- **Lifestyle scenes**: Fitness person, office desk, home setting, outdoor nature
- **Studio backgrounds**: Clean pedestal, gradient backdrop, minimalist surface
- **Themed environments**: Success/wealth, health/wellness, learning/growth

## How It Works

### Step 1: Generate Generic Scene (Current)
**AI generates background WITHOUT product:**

```
Input: "Generate lifestyle image for health supplement"
Output: Person in wellness setting with EMPTY SPACE ready for product
```

**Scene Types:**
- `product_hero`: Studio backdrop with empty pedestal/surface
- `lifestyle`: Natural scene with hands/person ready to hold product
- `comparison`: Split-screen before/after framework
- `infographic`: Abstract composition with designated product areas
- `social_post`: Eye-catching background with focal space

### Step 2: Automatic Text Removal
**Stability AI inpainting (~$0.01):**
- Removes any accidental text/artifacts
- Ensures clean, pristine background
- Ready for professional mockup overlay

### Step 3: Add Product Mockup (PRO/ENTERPRISE)
**Dynamic Mockups API (~$0.10):**
- User clicks "Create Mockup" on any scene
- Selects product template (bottle, box, book, course cover, etc.)
- Mockup overlays product onto scene with:
  - Realistic perspective and shadows
  - Curved text on bottle labels
  - Professional product placement
  - Photo-realistic integration

## Example Workflows

### Health Supplement Example
1. **Generate Scene**: Lifestyle photo of person exercising (no product)
2. **Clean Scene**: Remove any artifacts
3. **Add Mockup**: Overlay HepatoBurn supplement bottle in person's hand
4. **Reuse Scene**: Same scene + different supplement = new image

### Make Money Product Example
1. **Generate Scene**: Success-themed office desk background (no product)
2. **Clean Scene**: Pristine background ready
3. **Add Mockup**:
   - Course cover → Digital display mockup
   - eBook → Book mockup on desk
   - Software → Laptop screen mockup

### Coaching/Self-Help Example
1. **Generate Scene**: Inspirational outdoor setting (no product)
2. **Clean Scene**: Clean nature backdrop
3. **Add Mockup**:
   - Coaching program → Mobile app mockup
   - Workbook → Book mockup held in frame
   - Certification → Certificate frame mockup

## Scene Library Strategy

### Build Reusable Categories

#### **Wellness/Health Scenes**
- Gym/fitness environment
- Kitchen/healthy eating
- Yoga/meditation setting
- Outdoor active lifestyle
- Professional medical setting

#### **Success/Wealth Scenes**
- Modern office desk
- Entrepreneur working
- Luxury lifestyle setting
- Business meeting room
- Success celebration moment

#### **Learning/Growth Scenes**
- Study/learning environment
- Mentor/coaching setting
- Achievement moment
- Skill development scene
- Transformation visual

#### **Professional/Business Scenes**
- Corporate studio backdrop
- Team collaboration
- Professional presentation
- Expert authority setting
- Trust-building environment

## Product Categories Supported

### Physical Products
- **Supplements**: Bottles, boxes, packets
- **Books**: Physical books, workbooks, journals
- **Physical Products**: Any tangible product mockup

### Digital Products
- **Courses**: Course covers, module displays
- **eBooks**: Digital book covers
- **Software**: Screen mockups, app displays
- **Templates**: Document previews
- **Coaching Programs**: Program branding

### Services
- **Coaching**: Branding overlays
- **Consulting**: Service presentation
- **Events**: Event promotion graphics
- **Memberships**: Membership card/badge mockups

## Technical Implementation

### Image Generation (No Product)
```python
# Example prompt structure
prompt = "Professional studio backdrop with perfect lighting,
          clean minimalist background for product placement,
          empty pedestal ready for product,
          NO PRODUCTS in scene"
```

### Mockup Integration
```python
# Dynamic Mockups API call
POST /api/mockups/generate
{
  "image_url": "https://r2.dev/generic_studio_scene.png",
  "mockup_uuid": "supplement-bottle-3d",
  "smart_object_uuid": "front-label"
}
```

## Cost Comparison

### Old Approach (Product-Specific)
- Generate image with HepatoBurn bottle: $0.05
- Generate image with different supplement: $0.05
- Total for 2 products: **$0.10**

### New Approach (Generic + Mockup)
- Generate generic scene once: $0.05
- Clean scene: $0.01
- Add HepatoBurn mockup: $0.10
- Add different supplement mockup: $0.10
- **Total for 2 products: $0.26**
- **BUT**: Scene reusable for 100+ products = **$0.06 per image average**

### Scaling Benefits
- **10 products**: $0.016 per final image
- **100 products**: $0.006 per final image
- **1000 products**: $0.0006 per final image

## User Tiers

### FREE/BASIC
- Generate generic scenes
- Download for DIY mockup in Canva/Photoshop
- Manual product overlay

### PRO
- Generate generic scenes
- 5 professional mockups/month included
- $0.10 per additional mockup
- Automatic scene cleaning

### ENTERPRISE
- Generate generic scenes
- Unlimited professional mockups
- Automatic scene cleaning
- Priority mockup rendering

## Future Enhancements

### Scene Library Browser
- Searchable scene library
- Category filters
- Popular scenes ranking
- User favorites

### Smart Scene Recommendations
- AI suggests best scenes for product type
- Intelligence-based scene matching
- Style compatibility scoring

### Batch Mockup Generation
- Apply ONE scene to multiple products
- Bulk mockup creation
- Export as set

### Custom Scene Upload
- Users upload their own background scenes
- Scene validation and cleaning
- Personal scene library

## Migration Path

### Phase 1: Dual Mode (Current)
- Generate generic scenes by default
- Option to generate product-specific for legacy support

### Phase 2: Generic Only
- All new images are generic scenes
- Legacy product images still accessible
- Clear user education on new workflow

### Phase 3: Scene Library
- Curated library of premium scenes
- Instant scene selection
- No generation needed for common scenes

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-10-14
