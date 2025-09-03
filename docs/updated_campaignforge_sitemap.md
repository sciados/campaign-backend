# CampaignForge Project Sitemap

## Project Overview

CampaignForge is a comprehensive AI-powered marketing campaign creation platform with three main components:

- **Backend**: FastAPI-based intelligence and campaign management system
- **Frontend**: Next.js React application with TypeScript
- **AI Discovery Service**: Standalone service for AI platform monitoring and discovery

---

## 🎯 Backend (campaignforge-backend)

### Core Infrastructure

```
src/
├── core/
│   ├── app_factory.py              # FastAPI application factory
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database connection and session management
│   ├── security.py                 # Authentication and authorization
│   ├── credits.py                  # Credit system management
│   ├── responses.py                # Standardized API responses
│   └── router_registry.py          # Centralized route registration
```

### Authentication & User Management

```
src/
├── auth/
│   ├── routes.py                   # Login, logout, registration endpoints
│   └── dependencies.py            # Auth middleware and dependencies
├── models/
│   ├── user.py                     # User model and authentication
│   ├── company.py                  # Company/organization management
│   └── user_social_profile.py     # Social media profile integration
```

### Campaign Management System

```
src/campaigns/
├── routes/
│   ├── campaign_crud.py           # Campaign CRUD operations
│   ├── dashboard_stats.py         # Campaign performance analytics
│   ├── workflow_operations.py    # Campaign workflow management
│   ├── demo_management.py        # Demo campaign handling
│   └── admin_endpoints.py        # Admin campaign controls
├── schemas/
│   ├── campaign_schemas.py        # Campaign data validation
│   ├── workflow_schemas.py        # Workflow structure schemas
│   └── demo_schemas.py           # Demo campaign schemas
└── services/
    ├── campaign_service.py        # Core campaign business logic
    ├── workflow_service.py        # Workflow execution engine
    ├── demo_service.py           # Demo campaign service
    └── intelligence_service.py   # Campaign intelligence integration
```

### Intelligence System (Core AI Engine)

```
src/intelligence/
├── analyzers.py                   # Sales page and content analysis
├── handlers/
│   ├── intelligence_handler.py   # Main intelligence orchestration
│   ├── analysis_handler.py       # Analysis request handling
│   └── content_handler.py        # Content generation handling
├── amplifier/                    # AI enhancement system
│   ├── core.py                   # Core amplification engine
│   ├── ai_providers.py          # AI provider management
│   ├── enhancement.py           # Content enhancement logic
│   ├── service.py               # Amplification service layer
│   └── enhancements/            # Specific enhancement modules
│       ├── authority_enhancement.py
│       ├── credibility_enhancement.py
│       ├── emotional_enhancement.py
│       ├── market_enhancement.py
│       └── scientific_enhancement.py
└── utils/
    ├── smart_ai_balancer.py      # Load balancing across AI providers
    ├── tiered_ai_provider.py     # Cost-optimized AI routing
    ├── ultra_cheap_ai_provider.py # Budget AI provider system
    └── enhanced_rag_system.py    # Research augmented generation
```

### Content Generation Engine

```
src/intelligence/generators/
├── base_generator.py             # Base content generator class
├── email_generator.py            # Email campaign generation
├── ad_copy_generator.py          # Advertisement copy creation
├── blog_post_generator.py        # Blog content generation
├── social_media_generator.py     # Social media content
├── video_script_generator.py     # Video script creation
├── image_generator.py            # AI image generation
├── slideshow_video_generator.py  # Video slideshow creation
├── landing_page/                 # Landing page generation system
│   ├── core/generator.py         # Page generation engine
│   ├── templates/                # Page templates
│   ├── components/               # Reusable components
│   ├── analytics/                # Page performance tracking
│   └── variants/                 # A/B test variants
└── subject_line_ai_service.py    # Email subject line optimization
```

### Automation & Monitoring

```
src/intelligence/
├── automation/
│   └── niche_monitor.py          # Automated niche discovery and monitoring
├── proactive/
│   ├── sales_page_monitor.py     # Proactive sales page analysis
│   └── scheduler.py              # Task scheduling system
├── monitoring/
│   └── ai_monitor.py             # AI system health monitoring
├── cache/
│   ├── affiliate_optimized_cache.py  # Affiliate marketing cache
│   ├── global_cache.py           # Global caching system
│   └── shared_intelligence.py    # Shared intelligence cache
└── tasks/
    └── auto_analysis.py          # Background analysis tasks
```

### API Routes & Endpoints

```
src/intelligence/routers/
├── routes.py                     # Main intelligence routes
├── analysis_routes.py            # Analysis endpoint handlers
├── content_routes.py             # Content generation routes
├── analytics_routes.py           # Analytics and reporting
├── management_routes.py          # System management
├── proactive_analysis.py         # Proactive analysis endpoints
├── enhanced_intelligence_routes.py # Advanced intelligence features
├── smart_routing_routes.py       # AI provider routing
└── storage_routes.py             # File and content storage
```

### Storage & Media Management

```
src/
├── storage/
│   ├── universal_dual_storage.py # Multi-cloud storage system
│   ├── storage_tiers.py          # Tiered storage management
│   ├── document_manager.py       # Document handling
│   └── providers/
│       ├── cloudflare_r2.py      # Cloudflare R2 integration
│       └── backblaze_b2.py       # Backblaze B2 integration
└── media_generation/
    ├── services/
    │   ├── stability.py           # Stability AI integration
    │   ├── replicate.py          # Replicate AI integration
    │   └── fal.py                # FAL AI integration
    └── repository/repo.py         # Media asset management
```

### Database Models & CRUD

```
src/
├── models/
│   ├── intelligence.py           # Intelligence data models (NEW SCHEMA)
│   ├── campaign.py               # Campaign data models
│   ├── campaign_assets.py        # Campaign asset tracking
│   └── user_storage.py          # User file storage tracking
└── core/crud/
    ├── intelligence_crud.py      # Intelligence CRUD operations (UPDATED)
    ├── campaign_crud.py          # Campaign CRUD operations
    ├── user_crud.py              # User CRUD operations
    └── base_crud.py              # Base CRUD functionality
```

### Admin & Analytics

```
src/
├── admin/
│   ├── routes.py                 # Admin panel endpoints
│   └── services/
│       └── railway_env_service.py # Environment management
├── analytics/
│   └── routes.py                 # Analytics endpoints
└── dashboard/
    └── routes.py                 # Dashboard data endpoints
```

---

## 🌐 Frontend (campaignforge-frontend)

### Core Application Structure

```
src/
├── app/                          # Next.js 13+ app router
│   ├── layout.tsx               # Root layout component
│   ├── page.tsx                 # Landing page
│   ├── login/page.tsx           # Authentication pages
│   ├── register/page.tsx
│   └── onboarding/page.tsx      # User onboarding flow
```

### Dashboard System

```
src/app/dashboard/
├── page.tsx                     # Main dashboard router
├── analytics/page.tsx           # Analytics dashboard
├── content-library/page.tsx     # Content management
├── settings/page.tsx            # User settings
├── affiliate/                   # Affiliate marketer dashboard
│   ├── page.tsx
│   ├── commissions/page.tsx
│   └── competitors/page.tsx
├── business/page.tsx            # Business dashboard
├── creator/page.tsx             # Content creator dashboard
└── router/page.tsx              # Dashboard routing logic
```

### Campaign Management

```
src/app/campaigns/
├── page.tsx                     # Campaign listing
├── [id]/page.tsx               # Individual campaign view
├── [id]/settings/page.tsx      # Campaign settings
└── create-workflow/            # Campaign creation workflow
    ├── page.tsx
    ├── layout.tsx
    └── components/
        ├── Step1Selection.tsx   # Step 1: Campaign type selection
        ├── Step2Configuration.tsx # Step 2: Campaign configuration
        └── PlatformIntegration.tsx # Platform connection
```

### Admin Panel

```
src/app/admin/
├── page.tsx                    # Admin dashboard
└── components/
    ├── UserManagement.tsx      # User administration
    ├── CompanyManagement.tsx   # Company management
    ├── WaitlistManagement.tsx  # Waitlist administration
    ├── LiveAIToolsDashboard.tsx # AI tools monitoring
    ├── StorageMonitoring.tsx   # Storage usage monitoring
    └── ImageGenerationMonitoring.tsx # Media generation tracking
```

### UI Components

```
src/components/
├── ui/                         # Base UI components (shadcn/ui)
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   ├── tabs.tsx
│   └── ...
├── dashboards/                 # Dashboard components
│   ├── UserTypeRouter.tsx      # User type routing
│   ├── QuickActions.tsx        # Quick action buttons
│   ├── affiliate/AffiliateDashboard.tsx
│   ├── business/BusinessDashboard.tsx
│   └── creator/CreatorDashboard.tsx
├── campaigns/                  # Campaign components
│   ├── CampaignCard.tsx
│   ├── CampaignGrid.tsx
│   ├── CampaignFilters.tsx
│   ├── CreateCampaignModal.tsx
│   └── UniversalCampaignCreator.tsx
└── intelligence/               # Intelligence components
    ├── IntelligenceAnalyzer.tsx
    ├── ContentGenerator.tsx
    └── SalesPageIntelligenceEngine.tsx
```

### State Management & Services

```
src/lib/
├── stores/                     # Zustand state stores
│   ├── campaignStore.ts        # Campaign state management
│   ├── intelligenceStore.ts   # Intelligence data state
│   └── inputSourceStore.ts    # Input source management
├── services/
│   └── intelligenceWorkflowService.ts # Intelligence workflow logic
├── hooks/                      # Custom React hooks
│   ├── useUserType.ts         # User type management
│   └── useUserNavigation.ts   # Navigation helpers
└── types/                      # TypeScript type definitions
    ├── campaign.ts
    ├── intelligence.ts
    ├── api.ts
    └── auth.ts
```

### API Integration

```
src/lib/
├── api.ts                      # Main API client
├── ai-discovery-service.ts     # AI discovery service client
└── waitlist-api.ts            # Waitlist API client
```

---

## 🔍 AI Discovery Service (ai-discovery-service)

### Service Architecture

```
src/
├── main.py                     # FastAPI application entry point
├── api/
│   ├── routes.py              # Main API routes
│   └── ai_tools_routes.py     # AI tools specific endpoints
├── services/
│   ├── ai_tools_api.py        # AI tools API client
│   ├── ai_tools_monitor.py    # Monitoring and discovery
│   └── ai_tools_seeder.py     # Database seeding
├── models/
│   └── ai_tools_registry.py   # AI tools data models
└── database/
    ├── connection.py          # Database connectivity
    ├── init_db.py            # Database initialization
    └── models.py             # Database models
```

---

## 🗄️ Database Schema (New Optimized 6-Table Structure)

### Intelligence Core Tables

```sql
intelligence_core          -- Core intelligence metadata (lean)
├── id (Primary Key)
├── product_name
├── source_url
├── confidence_score
├── analysis_method
├── created_at
└── user_id, company_id (Foreign Keys)

product_data              -- Normalized product information
├── intelligence_id (Foreign Key)
├── features[]           -- Array of product features
├── benefits[]           -- Array of benefits
├── ingredients[]        -- Array of ingredients
├── conditions[]         -- Array of health conditions
└── usage_instructions[] -- Array of usage instructions

market_data              -- Market and positioning data
├── intelligence_id (Foreign Key)
├── category            -- Product category
├── positioning         -- Market positioning
├── competitive_advantages[] -- Array of advantages
└── target_audience     -- Target market description

knowledge_base           -- Centralized research repository
├── id (Primary Key)
├── content_hash        -- Deduplication hash
├── content            -- Research content
├── research_type      -- Type of research
├── source_metadata    -- Source information
└── created_at

intelligence_research    -- Links intelligence to research
├── intelligence_id (Foreign Key)
├── research_id (Foreign Key)
└── relevance_score    -- Relevance scoring

scraped_content         -- Deduplicated content cache
├── url_hash (Primary Key)
├── url
├── content
├── title
└── scraped_at
```

---

## 📁 Key File Relationships

### Schema Migration Files (Recently Updated)

- ✅ `src/intelligence/automation/niche_monitor.py` - **COMPLETED**
- ✅ `src/intelligence/proactive/sales_page_monitor.py` - **COMPLETED**  
- ✅ `src/intelligence/cache/affiliate_optimized_cache.py` - **COMPLETED**
- ✅ `src/intelligence/utils/enhanced_rag_system.py` - **COMPLETED**
- ✅ `src/core/crud/intelligence_crud.py` - **COMPLETED**

### Next Phase Files (Phase 3 - Application Logic)

- 🔄 `src/intelligence/generators/social_media_generator.py` - **NEEDS UPDATE**
- 🔄 `src/campaigns/routes/dashboard_stats.py` - **NEEDS UPDATE**
- 🔄 `src/intelligence/routers/content_routes.py` - **NEEDS UPDATE**
- 🔄 `src/intelligence/cache/global_cache.py` - **NEEDS UPDATE**
- 🔄 `src/intelligence/cache/shared_intelligence.py` - **NEEDS UPDATE**

---

## 🚀 Project Features

### Core Capabilities

- **AI-Powered Intelligence Analysis** - Sales page and competitor analysis
- **Multi-Platform Content Generation** - Emails, ads, social media, landing pages
- **Automated Niche Monitoring** - Real-time product discovery and analysis
- **Advanced Caching System** - 90% cost reduction through intelligent caching
- **RAG-Enhanced Research** - Research augmented generation for deeper insights
- **Tiered AI Provider System** - Cost-optimized AI routing and load balancing

### User Types & Dashboards

- **Affiliate Marketers** - Commission tracking, competitor analysis, product discovery
- **Business Owners** - Campaign management, ROI tracking, brand consistency
- **Content Creators** - Multi-format content generation, social media optimization

### Technical Highlights

- **Microservices Architecture** - Scalable, modular design
- **Advanced Database Optimization** - 90% storage reduction through normalization
- **Multi-Cloud Storage** - Redundant storage across Cloudflare R2 and Backblaze B2
- **Real-time Monitoring** - AI system health and performance tracking
- **Automated Workflows** - Background processing and proactive analysis

---

## 📊 Performance Metrics

- **90% Storage Reduction** - Through database schema optimization
- **95%+ Cache Hit Rate** - For affiliate marketing use cases  
- **Sub-$1 Cost Per Analysis** - Through intelligent AI provider routing
- **Real-time Processing** - Background automation and monitoring systems

---

*This sitemap represents the current state of CampaignForge as of Phase 2 completion of the intelligence schema migration. All core database operations have been updated to use the new optimized 6-table structure.*
