# Professional Mockup Generation - Tier-Based Feature

## Overview
Two-tier approach for image mockups:
- **FREE/BASIC Tier**: DIY clean images for manual editing
- **PRO/ENTERPRISE Tier**: Automatic professional mockups with Placeit API

## Backend Implementation (v3.5.0) ✅

### Files Created:
1. `src/storage/services/placeit_service.py` - Placeit API integration
2. `src/content/api/mockup_routes.py` - API endpoints for mockups

### API Endpoints:

#### POST `/api/mockups/generate`
Generate professional mockup from clean image
- **Requires**: PRO or ENTERPRISE tier
- **Cost**: $0.50 per mockup
- **Features**: Curved text, proper perspective, photo-realistic

**Request:**
```json
{
  "image_url": "https://r2.dev/images/clean_bottle.png",
  "template_id": "supplement_bottle_3d",
  "product_name": "HepatoBurn",
  "label_text": "Premium Liver Support"
}
```

**Response:**
```json
{
  "success": true,
  "mockup_url": "https://placeit.net/result/mockup123.jpg",
  "cost": 0.50,
  "template_id": "supplement_bottle_3d"
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
| PRO | 5 included | $0.50 each extra | Placeit API, curved text, templates |
| ENTERPRISE | Unlimited | Included | Placeit API, curved text, templates |

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
PLACEIT_API_KEY=your_placeit_api_key_here
```

## Deployment:
1. Backend pushed to GitHub ✅
2. Railway auto-deploy will pick up changes
3. Add `PLACEIT_API_KEY` to Railway environment variables
4. Test endpoints with Postman/curl
5. Build frontend UI

## Cost Estimation:
- Average user generates 2-3 mockups/month
- PRO tier: 5 included → $0 for most users
- Power users: 5 free + 3 extra = $1.50/month
- Very manageable costs with high perceived value

## Next Steps:
1. ✅ Backend API complete
2. ⏳ Add PLACEIT_API_KEY to Railway
3. ⏳ Create frontend mockup selector
4. ⏳ Add tier upgrade modal
5. ⏳ Test with real Placeit API
6. ⏳ Document for users

---

**Version**: 3.5.0
**Status**: Backend Complete, Frontend Pending
**Deployment**: Committed to main branch
