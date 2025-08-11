# CampaignForge Frontend Structure - Complete Sitemap
*Updated: August 10, 2025 - Frontend File Structure Analysis*

## Project Overview
CampaignForge frontend is a Next.js application with TypeScript, featuring a modern component-based architecture with dedicated stores for state management.

---

## 🎨 Frontend Structure (`/src`) - Complete File Structure

### Core Application Structure
```
src/
├── app/                           # Next.js App Router structure
│   ├── layout.tsx                 # Root layout component
│   ├── page.tsx                   # Home/landing page
│   ├── pagex.tsx                  # Alternative page implementation
│   ├── login/
│   │   └── page.tsx              # Login page
│   ├── register/
│   │   └── page.tsx              # Registration page
│   ├── dashboard/                 # Main dashboard section
│   │   ├── page.tsx              # Dashboard home
│   │   ├── analytics/
│   │   │   └── page.tsx          # Analytics dashboard
│   │   ├── campaigns/
│   │   │   └── page.tsx          # Campaigns management
│   │   ├── content-library/
│   │   │   └── page.tsx          # Content library view
│   │   └── settings/
│   │       └── page.tsx          # User settings
│   ├── campaigns/                 # Campaign management section
│   │   ├── page.tsx              # Campaigns list
│   │   ├── [id]/                 # Dynamic campaign routes
│   │   │   ├── page.tsx          # Individual campaign view
│   │   │   └── settings/
│   │   │       └── page.tsx      # Campaign settings
│   │   └── create-workflow/       # Campaign creation workflow
│   │       ├── layout.tsx        # Workflow layout
│   │       ├── page.tsx          # Workflow entry point
│   │       └── components/        # Workflow-specific components
│   │           ├── Step1Se...     # Step 1 component (truncated name)
│   │           └── Step2Co...     # Step 2 component (truncated name)
│   └── admin/                     # Admin panel
│       ├── page.tsx              # Admin dashboard
│       └── components/            # Admin-specific components
│           ├── CompanyManagement.tsx
│           ├── ImageGenerationMonitoring.tsx
│           ├── StorageMonitoring.tsx
│           ├── UserManagement.tsx
│           └── WaitlistManagement.tsx
```

### Component Library Structure
```
src/components/
├── ui/                           # Base UI components (shadcn/ui)
│   ├── alert.tsx
│   ├── badge.tsx
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   ├── label.tsx
│   ├── progress.tsx
│   └── tabs.tsx
├── admin/                        # Admin-specific components
│   ├── CompanyEditModal.tsx
│   └── UserEditModal.tsx
├── campaigns/                    # Campaign management components
│   ├── CampaignCard.tsx         # Individual campaign display
│   ├── CampaignFilters.tsx      # Filtering interface
│   ├── CampaignGrid.tsx         # Grid layout for campaigns
│   ├── CampaignStats.tsx        # Statistics display
│   ├── ContentViewEditModal.tsx # Content viewing/editing
│   ├── CreateCampaignModal.tsx  # Campaign creation modal
│   ├── SimpleCampaignModal.tsx  # Simplified campaign creation
│   └── UniversalCampaignCreator.tsx # Advanced campaign creator
├── dashboards/                   # Dashboard components
│   ├── CampaignDashboard.tsx    # Main campaign dashboard
│   ├── QuickActions.tsx         # Quick action buttons
│   └── RecentActivity.tsx       # Activity feed
├── input-sources/                # Input source management
│   ├── FileUploader.tsx         # File upload component
│   ├── InputSourceCard.tsx      # Source display card
│   ├── ProcessingQueue.tsx      # Processing status
│   ├── UniversalInputCollector...tsx # Input collection (truncated)
│   └── URLInputField.tsx        # URL input field
├── intelligence/                 # 🎯 CONTENT GENERATION COMPONENTS
│   ├── ContentGenerator.tsx     # 🔍 MAIN CONTENT GENERATOR
│   ├── ContentGenerator-v1.tsx  # Legacy version
│   ├── IntelligenceAnalyzer.tsx # Intelligence analysis
│   └── SalesPageIntelligenceEng...tsx # Sales page engine (truncated)
├── marketplace/                  # Marketplace components
│   ├── CategoryGrid.tsx         # Category display
│   └── ProductAccordion.tsx     # Product accordion
├── DemoPreferenceControl.tsx    # Demo preferences
├── ErrorBoundary.tsx            # Error handling
├── LoadingStates.tsx            # Loading components
└── WaitlistForm.tsx             # Waitlist signup
```

### State Management & API Layer
```
src/lib/
├── api.ts                       # 🔍 MAIN API CLIENT
├── waitlist-api.ts              # Waitlist API functions
├── utils.ts                     # Utility functions
├── stores/                      # State management
│   ├── campaignStore.ts         # Campaign state
│   ├── inputSourceStore.ts      # Input source state
│   └── intelligenceStore.ts     # 🔍 INTELLIGENCE/CONTENT STATE
└── types/                       # TypeScript type definitions
    ├── campaign.ts              # Campaign types
    ├── inputSource.ts           # Input source types
    ├── intelligence.ts          # 🔍 INTELLIGENCE TYPES
    └── output.ts                # Output/content types
```

### Configuration & Middleware
```
src/
├── middleware.ts                # Next.js middleware
└── types/
    └── index.ts                 # Global type definitions
```

---

## 🎯 **Key Files for Content Generation Issue**

### **Primary Investigation Targets:**
1. **`src/components/intelligence/ContentGenerator.tsx`** - Main content generation component
2. **`src/lib/api.ts`** - API client that makes the backend calls
3. **`src/lib/stores/intelligenceStore.ts`** - State management for content
4. **`src/lib/types/intelligence.ts`** - Type definitions for responses
5. **`src/lib/types/output.ts`** - Content output type definitions

### **Secondary Files:**
- **`src/components/intelligence/ContentGenerator-v1.tsx`** - Legacy implementation
- **`src/lib/stores/campaignStore.ts`** - Campaign state management
- **`src/components/campaigns/ContentViewEditModal.tsx`** - Content viewing component

---

## 🔍 **Analysis Summary**

The frontend follows a modern Next.js architecture with:

### **App Router Structure** (`/app`)
- Route-based organization
- Nested layouts and pages
- Dynamic routes for campaigns `[id]`
- Workflow-based campaign creation

### **Component Architecture** (`/components`)
- **UI Components**: shadcn/ui-based design system
- **Feature Components**: Organized by domain (campaigns, intelligence, admin)
- **Modal System**: Multiple modal components for different workflows

### **State Management** (`/lib/stores`)
- Separate stores for different domains
- TypeScript-first approach
- Centralized API client

### **Type Safety** (`/lib/types`)
- Comprehensive TypeScript definitions
- Domain-specific type files
- Strong typing for API responses

---

## 🎯 **Next Steps for Content Generation Fix**

To fix the "Content generation failed" error, we need to examine:

1. **ContentGenerator.tsx** - How it calls the API
2. **api.ts** - The actual API call implementation
3. **intelligenceStore.ts** - How it handles responses
4. **intelligence.ts & output.ts** - Expected response types

The issue is likely a mismatch between:
- **Backend response format** (what we just fixed)
- **Frontend expected format** (defined in types)
- **API client processing** (how api.ts handles responses)
- **Component error handling** (how ContentGenerator processes results)

This sitemap provides the roadmap for identifying and fixing the frontend-backend response format mismatch.
