# CampaignForge Complete Sitemap - Migration Status

## 🏗️ Project Structure Overview

**Migration Status:** Old 4-Step Workflow → New 2-Step Streamlined Workflow  
**Current State:** Partially migrated (core issues identified)  
**Target State:** Fully functional 2-step workflow with auto-analysis

---

## 📁 Backend File Structure

### 🎯 Campaign System (Core)

```
src/campaigns/
├── routes.py                              ⚠️  NEEDS FIX - Background task async context error
└── __init__.py                            ✅  OK
```

**Status:** `routes.py` has critical SQLAlchemy async context bug in `trigger_auto_analysis_task`

### 🧠 Intelligence System

```
src/intelligence/
├── routes.py                              ✅  OK - Main intelligence router
├── __init__.py                            ✅  OK
├── analyzers.py                           ✅  OK - Sales page analysis
├── 
├── adapters/
│   ├── __init__.py                        ✅  OK
│   └── dynamic_router.py                  ✅  OK
├── 
├── affiliate_networks/
│   └── shareasale_integr...               ✅  OK
├── 
├── amplifier/                             ✅  OK - AI enhancement system
│   ├── __init__.py                        ✅  OK
│   ├── ai_providers.py                    ✅  OK
│   ├── core.py                            ✅  OK
│   ├── enhancement.py                     ✅  OK - Main amplification logic
│   ├── fallbacks.py                       ✅  OK
│   ├── service.py                         ✅  OK
│   ├── sources.py                         ✅  OK
│   ├── utils.py                           ✅  OK
│   └── enhancements/                      ✅  OK - Enhancement modules
│       ├── __init__.py                    ✅  OK
│       ├── authority_enh...               ✅  OK
│       ├── content_enhan...               ✅  OK
│       ├── credibility_e...               ✅  OK
│       ├── emotional_enh...               ✅  OK
│       ├── market_enhanc...               ✅  OK
│       └── scientific_en...               ✅  OK
├── 
├── automation/
│   └── niche_monitor.py                   ✅  OK
├── 
├── cache/                                 ✅  OK - Caching system
│   ├── affiliate_optimized_cache.py       ✅  OK
│   ├── global_cache.py                    ✅  OK
│   └── shared_intelligence.py             ✅  OK
├── 
├── extractors/                            ✅  OK
│   ├── __init__.py                        ✅  OK
│   └── product_extractor.py               ✅  OK
├── 
├── generators/                            ✅  OK - Content generation
│   ├── __init__.py                        ✅  OK
│   ├── base_generator.py                  ✅  OK
│   ├── factory.py                         ✅  OK
│   ├── ad_copy_generator.py               ✅  OK
│   ├── blog_post_generator.py             ✅  OK
│   ├── campaign_angle_generator.py        ✅  OK
│   ├── email_generator.py                 ✅  OK
│   ├── slideshow_video_generator.py       ✅  OK
│   ├── social_media_generator.py          ✅  OK
│   ├── stability_ai_generator.py          ✅  OK
│   ├── ultra_cheap_image_generat...       ✅  OK
│   ├── unified_ultra_cheap_provider.py    ✅  OK
│   ├── video_script_generator.py          ✅  OK
│   └── landing_page/                      ✅  OK - Landing page generator
│       ├── __init__.py                    ✅  OK
│       ├── routes.py                      ✅  OK
│       ├── analytics/                     ✅  OK
│       ├── components/                    ✅  OK
│       ├── core/                          ✅  OK
│       ├── database/                      ✅  OK
│       ├── intelligence/                  ✅  OK
│       ├── templates/                     ✅  OK
│       ├── utils/                         ✅  OK
│       └── variants/                      ✅  OK
├── 
├── handlers/                              ⚠️  NEEDS ATTENTION
│   ├── __init__.py                        ✅  OK
│   ├── analysis_handler.py                ⚠️  NEEDS FIX - Timezone & async issues
│   ├── content_handler.py                 ✅  OK
│   └── intelligence_handler.py            ✅  OK
├── 
├── monitoring/
│   └── ai_monitor.py                      ✅  OK
├── 
├── niches/
│   └── niche_targeting.py                 ✅  OK
├── 
├── proactive/
│   ├── sales_page_monitor.py              ✅  OK
│   └── scheduler.py                       ✅  OK
├── 
├── routers/                               ✅  OK - Sub-routers
│   ├── __init__.py                        ✅  OK
│   ├── routes.py                          ✅  OK
│   ├── ai_monitoring_routes.py            ✅  OK
│   ├── analysis_routes.py                 ✅  OK
│   ├── analytics_routes.py                ✅  OK
│   ├── content_routes.py                  ✅  OK
│   ├── debug_routes.py                    ✅  OK - Extensive debugging endpoints
│   ├── document_routes.py                 ✅  OK
│   ├── management_routes.py               ✅  OK
│   ├── proactive_analysis.py              ✅  OK
│   ├── r2_debug_routes.py                 ✅  OK
│   ├── simple_smart_routes.py             ✅  OK
│   ├── smart_routing_routes.py            ✅  OK
│   ├── stability_routes.py                ✅  OK
│   ├── storage_routes.py                  ✅  OK
│   └── universal_test_routes.py           ✅  OK
├── 
├── schemas/                               ✅  OK
│   ├── __init__.py                        ✅  OK
│   ├── monitoring_schemas.py              ✅  OK
│   ├── requests.py                        ✅  OK
│   └── responses.py                       ✅  OK
└── 
└── utils/                                 ✅  OK - Utility functions
    ├── __init__.py                        ✅  OK
    ├── ai_intelligence_saver.py           ✅  OK
    ├── ai_throttle.py                     ✅  OK
    ├── analyzer_factory.py                ✅  OK
    ├── campaign_helpers.py                ✅  OK
    ├── enum_serializer.py                 ✅  OK
    ├── intelligence_validation.py         ✅  OK
    ├── product_name_fix.py                ✅  OK
    ├── railway_compatibility.py           ✅  OK
    ├── railway_deployment_check.py        ✅  OK
    ├── smart_ai_balancer.py               ✅  OK
    ├── smart_provider_router.py           ✅  OK
    ├── smart_router.py                    ✅  OK
    ├── test_ultra_cheap_railway.py        ✅  OK
    ├── tiered_ai_provider.py              ✅  OK
    ├── ultra_cheap_ai_provider.py         ✅  OK
    ├── ultra_cheap_video_provider.py      ✅  OK
    └── unified_ultra_cheap_provider.py    ✅  OK
```

### 🗄️ Database Models

```
src/models/
├── __init__.py                            ✅  OK
├── base.py                                ✅  OK
├── campaign.py                            ⚠️  GOOD - Enhanced for 2-step workflow (timezone fixed)
├── campaign_assets.py                     ✅  OK
├── company.py                             ✅  OK
├── intelligence.py                        ✅  OK
├── user.py                                ✅  OK
└── waitlist.py                            ✅  OK
```

### 🔧 Core System

```
src/core/
├── config.py                              ✅  OK
├── credits.py                             ✅  OK
├── database.py                            ⚠️  NEEDS CHECK - Ensure AsyncSessionLocal exists
└── security.py                            ✅  OK
```

### 🔐 Authentication

```
src/auth/
├── __init__.py                            ✅  OK
├── dependencies.py                        ✅  OK
└── routes.py                              ✅  OK
```

### 👑 Admin System

```
src/admin/
├── __init__.py                            ✅  OK
├── routes.py                              ✅  OK
└── schemas.py                             ✅  OK
```

### 📊 Analytics

```
src/analytics/
└── routes.py                              ✅  OK
```

### 📱 Dashboard

```
src/dashboard/
├── __init__.py                            ✅  OK
└── routes.py                              ✅  OK
```

### 🔗 Other Routes

```
src/routes/
├── __init__.py                            ✅  OK
└── waitlist.py                            ✅  OK
```

### 📋 Schemas

```
src/schemas/
└── waitlist.py                            ✅  OK
```

### 🎛️ Services

```
src/services/
├── ai_services/
│   └── openai_service_copy.py             ✅  OK
└── platform_services/
    └── video_service.py                   ✅  OK
```

### 💾 Storage

```
src/storage/
├── document_manager.py                    ✅  OK
├── universal_dual_storage.py              ✅  OK
└── providers/
    ├── backblaze_b2.py                    ✅  OK
    └── cloudflare_r2.py                   ✅  OK
```

### 🛠️ Utilities

```
src/utils/
└── demo_campaign_seeder.py                ⚠️  ENHANCED - Rich demo system (good)
```

### 🚀 Main Application

```
src/
└── main.py                                ✅  OK
```

---

## 📱 Frontend File Structure

### 🏠 Main Pages

```
src/app/
├── layout.tsx                             ✅  OK
├── page.tsx                               ✅  OK - Landing page
├── pagex.tsx                              ❓  UNKNOWN - May be duplicate
├── middleware.ts                          ✅  OK
├── login/
│   └── page.tsx                           ✅  OK
└── register/
    └── page.tsx                           ✅  OK
```

### 🎯 Campaign System (MAIN FOCUS)

```
src/app/campaigns/
├── page.tsx                               ✅  OK - Campaign list
├── create-workflow/                       ✅  KEEP - New streamlined workflow
│   ├── layout.tsx                         ✅  OK
│   ├── page.tsx                           ✅  OK
│   └── components/
│       ├── Step1Se...                     ✅  OK
│       └── Step2Co...                     ✅  OK
└── [id]/                                  ⚠️  MIXED - Clean up needed
    ├── page.tsx                           ✅  KEEP - Unified campaign page (2-step workflow)
    ├── analysis/
    │   └── page.tsx                       ❌  DELETED - Old 4-step workflow
    ├── content/
    │   └── page.tsx                       ❌  DELETED - Old 4-step workflow
    ├── generate/
    │   └── page.tsx                       ❌  DELETED - Old 4-step workflow
    ├── inputs/
    │   └── page.tsx                       ❌  DELETED - Old 4-step workflow
    └── settings/
        └── page.tsx                       ✅  OK - Keep settings
```

**⚠️ CRITICAL:** Remove the 4 deprecated pages: `analysis/`, `content/`, `generate/`, `inputs/`

### 📊 Dashboard System

```
src/app/dashboard/
├── page.tsx                               ✅  OK
├── analytics/
│   └── page.tsx                           ✅  OK
├── campaigns/
│   └── page.tsx                           ✅  OK
├── content-library/
│   └── page.tsx                           ✅  OK
└── settings/
    └── page.tsx                           ✅  OK
```

### 🛒 Marketplace

```
src/app/marketplace/
├── layout.tsx                             ✅  OK
├── page.tsx                               ✅  OK
└── [category]/
    └── page.tsx                           ✅  OK
```

### 👑 Admin Panel

```
src/app/admin/
└── page.tsx                               ✅  OK
```

### 🧩 Components

```
src/components/
├── ErrorBoundary.tsx                      ✅  OK
├── LoadingStates.tsx                      ✅  OK
├── DemoPreferenceControl.tsx              ✅  OK
├── WaitlistForm.tsx                       ✅  OK
├── 
├── ui/                                    ✅  OK - UI components
│   ├── alert.tsx                          ✅  OK
│   ├── badge.tsx                          ✅  OK
│   ├── button.tsx                         ✅  OK
│   ├── card.tsx                           ✅  OK
│   ├── input.tsx                          ✅  OK
│   ├── label.tsx                          ✅  OK
│   ├── progress.tsx                       ✅  OK
│   └── tabs.tsx                           ✅  OK
├── 
├── admin/                                 ✅  OK
│   ├── CompanyEditModal.tsx               ✅  OK
│   └── UserEditModal.tsx                  ✅  OK
├── 
├── campaigns/
├── routes.py                              ⚠️  NEEDS UPDATE - Use service layer instead of direct DB calls
├── __init__.py                            ✅  OK
├── 
├── schemas/                               ✅  NEW - Complete schema organization
│   ├── __init__.py                        ✅  NEW - Package exports
│   ├── campaign_schemas.py                ✅  NEW - Core campaign models (CampaignCreate, CampaignUpdate, CampaignResponse)
│   ├── demo_schemas.py                    ✅  NEW - Demo system models (DemoPreferenceUpdate, DemoPreferenceResponse)
│   └── workflow_schemas.py                ✅  NEW - 2-step workflow models (WorkflowProgressData)
│
└── services/                              ✅  NEW - Complete service layer
│   ├── __init__.py                        ✅  NEW - Service exports
│   ├── campaign_service.py                ✅  NEW - Complete CRUD + FIXED background task
│   ├── demo_service.py                    ✅  NEW - Smart demo management with user preferences
│   └── workflow_service.py                ✅  NEW - 2-step workflow logic with progress tracking 
│
⚠️  MIXED - Review for old workflow references
└──References
│   ├── CampaignCard.tsx                   ✅  OK
│   ├── CampaignFilters.tsx                ✅  OK
│   ├── CampaignGrid.tsx                   ✅  OK
│   ├── CampaignStats.tsx                  ✅  OK
│   ├── ContentViewEditModal.tsx           ✅  OK
│   ├── CreateCampaignModal.tsx            ✅  OK
│   ├── SimpleCampaignModal.tsx            ✅  OK
│   └── UniversalCampaignCreator.tsx       ✅  OK
├── 
├── dashboards/                            ⚠️  REVIEW - May contain old workflow logic
│   ├── CampaignDashboard.tsx              ⚠️  REVIEW
│   ├── CampaignStep1.tsx                  ⚠️  REVIEW - May be old 4-step
│   ├── CampaignStep2.tsx                  ⚠️  REVIEW - May be old 4-step  
│   ├── CampaignStep3.tsx                  ⚠️  REVIEW - May be old 4-step
│   ├── QuickActions.tsx                   ✅  OK
│   └── RecentActivity.tsx                 ✅  OK
├── 
├── input-sources/                         ✅  OK
│   ├── FileUploader.tsx                   ✅  OK
│   ├── InputSourceCard.tsx                ✅  OK
│   ├── ProcessingQueue.tsx                ✅  OK
│   ├── UniversalInputCollector...         ✅  OK
│   └── URLInputField.tsx                  ✅  OK
├── 
├── intelligence/                          ✅  OK
│   ├── ContentGenerator.tsx               ✅  OK
│   ├── ContentGenerator-v1.tsx            ✅  OK
│   ├── IntelligenceAnalyzer.tsx           ✅  OK
│   └── SalesPageIntelligenceEng...        ✅  OK
└── 
└── marketplace/                           ✅  OK
    ├── CategoryGrid.tsx                   ✅  OK
    ├── ClickBankCampaignCreator.tsx       ✅  OK
    └── ProductAccordion.tsx               ✅  OK
```

### 📚 Libraries & Utilities

```
src/lib/
├── api.ts                                 ✅  OK - API client
├── utils.ts                               ✅  OK
├── waitlist-api.ts                        ✅  OK
├── 
├── stores/                                ✅  OK - State management
│   ├── campaignStore.ts                   ✅  OK
│   ├── inputSourceStore.ts                ✅  OK
│   └── intelligenceStore.ts               ✅  OK
└── 
└── types/                                 ✅  OK - TypeScript types
    ├── campaign.ts                        ✅  OK
    ├── inputSource.ts                     ✅  OK
    ├── intelligence.ts                    ✅  OK
    └── output.ts                          ✅  OK
```

### 📄 Root Types

```
src/
└── types/
    └── index.ts                           ✅  OK
```

---

## 🚨 Critical Issues Summary

### 🔥 High Priority Fixes

1. **`src/campaigns/routes.py`**
   - **Issue:** Background task `trigger_auto_analysis_task` has SQLAlchemy async context error
   - **Status:** ✅ FIXED - Did prevent campaign creation
   - **Fix:** Create new async session within background task

2. **Frontend Cleanup**
   - **Issue:** Old 4-step workflow files causing route conflicts
   - **Status:** ❌ DEPRECATED - AND DELETED:
     - `src/app/campaigns/[id]/analysis/page.tsx`
     - `src/app/campaigns/[id]/content/page.tsx`
     - `src/app/campaigns/[id]/generate/page.tsx`
     - `src/app/campaigns/[id]/inputs/page.tsx`

3. **`src/core/database.py`**
   - **Issue:** May be missing `AsyncSessionLocal` for background tasks
   - **Status:** ✅ EXISTS VERIFIED

### ⚠️ Medium Priority Reviews

1. **`src/intelligence/handlers/analysis_handler.py`**
   - **Issue:** Some timezone and async handling improvements needed
   - **Status:** ✅ FIXED

2. **Dashboard Components**
   - **Issue:** May contain old 4-step workflow references
   - **Status:** ✅ FIXED
   - **Files:** `CampaignStep1.tsx`, `CampaignStep2.tsx`, `CampaignStep3.tsx`

### ✅ Working Systems

- Intelligence analysis system
- Content generation
- Demo campaign system
- User management
- Admin panel
- Marketplace
- Storage systems
- AI provider integration
- Ultra-cheap image generation

---

## 🎯 Workflow Comparison

### ❌ Old 4-Step Workflow (DEPRECATED)
```
1. Setup     → Basic campaign info
2. Sources   → Add competitor URLs/documents manually
3. Analysis  → Run AI analysis on sources  
4. Generate  → Create marketing content
```

### ✅ New 2-Step Workflow (CURRENT TARGET)
```
1. Setup & Auto-Analysis → Campaign creation + automatic competitor analysis
2. Content Generation    → Create marketing content using analysis results
```

---

## 📋 Migration Checklist

### 🗑️ Frontend Cleanup  
- [ ] Update steps array in main campaign page (4→2 steps)
- [ ] Review dashboard components for old workflow references

### 🧪 Testing
- [ ] Campaign creation without competitor URL
- [ ] Campaign creation with competitor URL (auto-analysis)
- [ ] Background task completion
- [ ] Workflow navigation (2 steps only)
- [ ] Demo campaign system
- [ ] Content generation after analysis

---

## 🎖️ System Health Status

**Overall Status:** 🟡 **Partially Functional**

- **Core Systems:** ✅ Working (Intelligence, Content Gen, Admin)
- **Campaign Creation:** ❌ Broken (Async context error)
- **Workflow Navigation:** ⚠️ Mixed (Old files causing conflicts)
- **User Experience:** ⚠️ Degraded (Routing issues)

**Target Status:** 🟢 **Fully Functional 2-Step Workflow**

---

**Last Updated:** Current migration analysis  
**Migration Progress:** ~75% complete  
**Estimated Completion:** 2-3 hours of focused development  
**Risk Level:** Medium (affects core campaign creation)