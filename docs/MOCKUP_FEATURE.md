# Professional Mockup Generation - Tier-Based Feature

## Overview
Two-tier approach for image mockups:
- **FREE/BASIC Tier**: DIY clean images for manual editing
- **PRO/ENTERPRISE Tier**: Automatic professional mockups with Dynamic Mockups API

## Backend Implementation (v3.5.0) ✅

### Files Created:
1. `src/storage/services/dynamic_mockups_service.py` - Dynamic Mockups API integration
2. `src/storage/services/inpainting_service.py` - Automatic text removal via AI inpainting
3. `src/content/api/mockup_routes.py` - API endpoints for mockups

### API Endpoints:

#### POST `/api/mockups/generate`
Generate professional mockup from clean image
- **Requires**: PRO or ENTERPRISE tier
- **Cost**: ~$0.10 per mockup
- **Features**: Fast rendering (~1s), custom templates, photo-realistic
- **Provider**: Dynamic Mockups API

**Request:**
```json
{
  "image_url": "https://r2.dev/images/clean_bottle.png",
  "mockup_uuid": "supplement-bottle-3d-front",
  "smart_object_uuid": "front-label",
  "product_name": "HepatoBurn",
  "label_text": "Premium Liver Support"
}
```

**Response:**
```json
{
  "success": true,
  "mockup_url": "https://dynamicmockups.com/result/mockup123.jpg",
  "cost": 0.10,
  "mockup_uuid": "supplement-bottle-3d-front"
}
```

**Tier Rejection (FREE/BASIC):**
```json
{
  "success": false,
  "error": "Mockup generation requires PRO or ENTERPRISE tier",
  "upgrade_required": true,
  "feature": "professional_mockups"
}
```

#### GET `/api/mockups/templates`
List available mockup templates
- **Parameters**: `category` (supplement, lifestyle, packaging)
- **Returns**: Template list + user tier + limits

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "id": "supplement_bottle_3d",
      "name": "3D Supplement Bottle",
      "description": "Photo-realistic supplement bottle with custom label",
      "preview_url": "https://placeit.net/templates/preview.jpg"
    }
  ],
  "user_tier": "PRO",
  "tier_limits": {
    "allowed": true,
    "monthly_limit": 5,
    "cost_per_additional": 0.50,
    "message": "5 mockups included, $0.50 each additional"
  }
}
```

#### GET `/api/mockups/tier-info`
Get user's tier limits and pricing

**Response:**
```json
{
  "success": true,
  "user_tier": "PRO",
  "limits": {
    "allowed": true,
    "monthly_limit": 5,
    "cost_per_additional": 0.50,
    "message": "5 mockups included, $0.50 each additional"
  },
  "feature": "professional_mockups"
}
```

## Tier Access Matrix

| Tier | Mockups/Month | Cost | Features |
|------|---------------|------|----------|
| FREE | 0 | N/A | Clean images only, DIY editing |
| BASIC | 0 | N/A | Clean images only, DIY editing |
| PRO | 5 included | $0.10 each extra | Dynamic Mockups API, fast rendering, templates |
| ENTERPRISE | Unlimited | Included | Dynamic Mockups API, fast rendering, templates |

## Template Categories

### Supplement Category:
- `supplement_bottle_3d` - 3D supplement bottle with custom label
- `supplement_bottle_flat` - Flat lay with natural elements
- `supplement_box_mockup` - Product box with custom design
- `supplement_label_closeup` - Close-up with depth

### Lifestyle Category:
- `hand_holding_bottle` - Person holding bottle
- `gym_scene_bottle` - Fitness setting

## Frontend TODO (Next Phase):

### For FREE/BASIC Users:
1. Download clean image button
2. Link to Canva/Photoshop tutorials
3. Upgrade prompt with PRO benefits

### For PRO/ENTERPRISE Users:
1. Mockup template selector modal
2. Product name/label text inputs
3. Preview mockup before generating
4. Usage counter (X/5 mockups used this month)
5. Cost display for additional mockups

### Upgrade Flow:
1. Show mockup templates to all users
2. Lock PRO templates with upgrade badge
3. Click locked template → upgrade modal
4. Show pricing and benefits

## Environment Variables Required:

```bash
DYNAMIC_MOCKUPS_API_KEY=your_dynamic_mockups_api_key_here
STABILITY_API_KEY=your_stability_api_key_here  # For automatic text removal
```

Get your API keys:
- Dynamic Mockups: https://app.dynamicmockups.com/dashboard-api
- Stability AI: https://platform.stability.ai/account/keys

## Deployment:
1. Backend pushed to GitHub ✅
2. Railway auto-deploy will pick up changes
3. Add `DYNAMIC_MOCKUPS_API_KEY` to Railway environment variables
4. `STABILITY_API_KEY` already configured ✅
5. Test endpoints with Postman/curl
6. Build frontend UI

## Cost Estimation:
- Average user generates 2-3 mockups/month
- PRO tier: 5 included → $0 for most users
- Power users: 5 free + 3 extra = $0.30/month
- Image cleaning: ~$0.01 per image (automatic text removal)
- Very manageable costs with high perceived value
- Dynamic Mockups plans start at $19/month for platform subscription

## Next Steps:
1. ✅ Backend API complete (Dynamic Mockups integration)
2. ✅ Automatic text removal integrated (Stability AI)
3. ⏳ Add DYNAMIC_MOCKUPS_API_KEY to Railway
4. ⏳ Create frontend mockup selector
5. ⏳ Add tier upgrade modal
6. ⏳ Test with real Dynamic Mockups API
7. ⏳ Document for users

---

**Version**: 3.6.0
**Provider**: Dynamic Mockups API (replaced Placeit)
**Status**: Backend Complete, Frontend Pending
**Deployment**: Committed to main branch
