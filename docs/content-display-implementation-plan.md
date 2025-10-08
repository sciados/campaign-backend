# Content Type Display & Manipulation Implementation Plan

## Overview

Each content type requires tailored display and editing experiences based on its unique structure and use cases. This document outlines the complete implementation plan for all content types.

---

## Content Type Specifications

### 1. Email Sequence

**Current State:** ✅ Has dedicated display (basic implementation)

**Data Structure:**
```json
{
  "emails": [
    {
      "email_number": 1,
      "subject": "...",
      "body": "...",
      "send_delay": "Day 1",
      "psychology_stage": "problem_agitation"
    }
  ]
}
```

**Display Requirements:**
- Individual email preview cards with email number
- Subject line prominently displayed
- Email body with proper formatting
- Send delay timeline visualization
- Psychology stage indicator

**Manipulation Features:**
- ✏️ Inline subject line editing with character count
- ✏️ Body text editing with formatting tools
- 📋 Copy individual emails or entire sequence
- 🎨 Email template preview (HTML mockup)
- 🔄 Reorder emails in sequence (drag & drop)
- ⏰ Adjust send delay timing
- 💾 Export to ESP formats:
  - Mailchimp
  - ActiveCampaign
  - ConvertKit
  - Custom CSV

**Technical Implementation:**
```typescript
interface EmailDisplay {
  showTimeline: boolean;
  editMode: boolean;
  exportFormat: 'html' | 'plaintext' | 'csv';
}
```

---

### 2. Ad Copy

**Current State:** ✅ Has dedicated display (recently implemented)

**Data Structure:**
```json
{
  "ads": [
    {
      "variation_number": 1,
      "platform": "google",
      "ad_format": "responsive",
      "headlines": ["..."],
      "descriptions": ["..."],
      "primary_text": "...",
      "call_to_action": "...",
      "compliance_status": {...}
    }
  ]
}
```

**Display Requirements:**
- Variation cards with platform/format badges
- Headlines with character count (X/30)
- Descriptions with character count (X/90)
- Primary text in highlighted section
- Call-to-action badge
- Compliance status indicator

**Manipulation Features:**
- 📋 One-click copy per headline/description/element
- ✏️ Inline editing with real-time character count
- ⚠️ Character limit validation with warnings
- 🎨 Platform preview mockups:
  - Google Ads preview
  - Facebook Ads preview
  - LinkedIn Ads preview
- 🔄 A/B test variant creator
- 📱 Mobile vs Desktop preview toggle
- 💾 Export to platform-specific formats:
  - Google Ads CSV
  - Facebook Ads JSON
  - LinkedIn Campaign Manager CSV

**Technical Implementation:**
```typescript
interface AdCopyDisplay {
  platform: 'google' | 'facebook' | 'linkedin' | 'instagram';
  previewMode: 'mobile' | 'desktop';
  editMode: boolean;
  validateCompliance: boolean;
}
```

---

### 3. Blog Post / Article

**Current State:** ❌ Generic display (needs implementation)

**Data Structure:**
```json
{
  "article": {
    "title": "...",
    "content": "...",
    "meta_description": "...",
    "keywords": ["..."],
    "reading_time": "...",
    "word_count": 1500
  }
}
```

**Display Requirements:**
- Article title as H1
- Rich text content with proper formatting
- Reading time estimate
- Word count
- Meta description preview
- Keyword tags
- Table of contents (auto-generated from headings)

**Manipulation Features:**
- 📰 Rich text editor with formatting toolbar
- ✏️ Markdown or WYSIWYG editing modes
- 🖼️ Featured image upload/placeholder
- 🏷️ SEO fields:
  - Meta title (60 chars)
  - Meta description (160 chars)
  - Focus keyword
  - Slug/URL
- 📋 Copy entire article or sections
- 🎨 Blog layout preview with:
  - Desktop view
  - Mobile view
  - Reading mode
- 📊 Content analysis:
  - Readability score (Flesch-Kincaid)
  - SEO optimization score
  - Keyword density
  - Internal linking suggestions
  - Heading structure validation
- 💾 Export formats:
  - WordPress (XML)
  - Medium (HTML)
  - Markdown (.md)
  - HTML
  - Plain text
  - PDF

**Technical Implementation:**
```typescript
interface BlogPostDisplay {
  editMode: boolean;
  editorType: 'wysiwyg' | 'markdown' | 'raw';
  showSEOPanel: boolean;
  previewMode: 'desktop' | 'mobile' | 'reader';
  seoChecks: {
    readability: number;
    seoScore: number;
    keywordDensity: number;
  };
}
```

---

### 4. Social Media Posts

**Current State:** ❌ Generic display (needs implementation)

**Data Structure:**
```json
{
  "posts": [
    {
      "platform": "twitter",
      "content": "...",
      "hashtags": ["..."],
      "character_count": 280,
      "media_type": "image",
      "best_time_to_post": "..."
    }
  ]
}
```

**Display Requirements:**
- Platform-specific post cards
- Platform icon/badge
- Content with hashtag highlighting
- Character count with platform limit
- Media preview placeholder
- Best posting time suggestion

**Manipulation Features:**
- 📱 Platform-specific previews:
  - Twitter/X card mockup (280 chars)
  - LinkedIn post mockup (3000 chars)
  - Instagram caption mockup (2200 chars)
  - Facebook post mockup (63,206 chars)
  - TikTok caption mockup (2200 chars)
- 💬 Real-time character count per platform
- #️⃣ Hashtag recommendations based on:
  - Trending topics
  - Industry relevance
  - Engagement history
- ✏️ Inline editing with platform-specific limits
- 🖼️ Image attachment preview/upload
- ⏰ Best time to post suggestions (ML-based)
- 📋 Copy for each platform with optimal formatting
- 🔄 Cross-post scheduler with platform optimization
- 💾 Export formats:
  - Social media management tools (Buffer, Hootsuite)
  - CSV for bulk scheduling
  - Individual platform APIs

**Technical Implementation:**
```typescript
interface SocialMediaDisplay {
  platform: 'twitter' | 'linkedin' | 'facebook' | 'instagram' | 'tiktok';
  showPreview: boolean;
  editMode: boolean;
  hashtagRecommendations: string[];
  postingSchedule: {
    suggested_time: Date;
    timezone: string;
  };
}
```

---

### 5. Video Script

**Current State:** ❌ Generic display (needs implementation)

**Data Structure:**
```json
{
  "script": {
    "title": "...",
    "duration": "2:30",
    "scenes": [
      {
        "scene_number": 1,
        "duration": "0:15",
        "shot_type": "Wide shot",
        "dialogue": "...",
        "action": "...",
        "music": "Upbeat background",
        "sfx": "Door opening"
      }
    ]
  }
}
```

**Display Requirements:**
- Script title and total duration
- Scene-by-scene breakdown
- Shot descriptions
- Dialogue with character labels
- Action/direction notes
- Music and SFX cues
- Cumulative time markers

**Manipulation Features:**
- 🎬 Professional script format view:
  - INT./EXT. scene headings
  - Action descriptions
  - Character names (centered)
  - Dialogue (centered, narrower)
  - Parentheticals
  - Transitions
- ⏱️ Duration calculator:
  - Per scene
  - Per dialogue line
  - Total runtime
- 🎭 Character/speaker labels with color coding
- 📹 Shot type indicators (Wide, Close-up, POV, etc.)
- 🎵 Audio cues section:
  - Background music
  - Sound effects
  - Voiceover notes
- ✏️ Scene-by-scene editing with:
  - Drag & drop scene reordering
  - Inline text editing
  - Duration adjustment
- 📋 Copy options:
  - Entire script
  - Individual scenes
  - Dialogue only
  - Action only
- 🎬 Storyboard preview (if images available)
- 💾 Export formats:
  - Final Draft (.fdx)
  - Fountain (.fountain)
  - PDF (formatted screenplay)
  - Teleprompter format (.txt)
  - Celtx XML
  - Plain text

**Technical Implementation:**
```typescript
interface VideoScriptDisplay {
  formatType: 'screenplay' | 'teleprompter' | 'storyboard';
  showTimings: boolean;
  showAudioCues: boolean;
  editMode: boolean;
  durationEstimate: {
    perScene: number[];
    total: number;
  };
}
```

---

### 6. Marketing Images

**Current State:** ✅ Has dedicated display (basic implementation)

**Data Structure:**
```json
{
  "image_url": "...",
  "prompt": "...",
  "dimensions": {
    "width": 1024,
    "height": 1024
  },
  "style": "photorealistic"
}
```

**Display Requirements:**
- Full-size image display
- Image dimensions
- Generation prompt
- Style/model used
- Download button

**Manipulation Features:**
- 🖼️ Full-size lightbox view with zoom
- 📋 Copy image URL to clipboard
- 💾 Download in multiple formats:
  - PNG (lossless)
  - JPG (compressed)
  - WebP (optimized)
- 📐 Resize/crop tool:
  - Social media presets (1200x630, 1080x1080, etc.)
  - Custom dimensions
  - Aspect ratio lock
- ✏️ Regenerate with prompt editing:
  - Edit original prompt
  - Add style modifiers
  - Adjust parameters
- 🎨 Style variations generator:
  - Same subject, different styles
  - Color variations
  - Composition variations
- 🔄 Upscale image (2x, 4x)
- 🖌️ AI editing tools:
  - Inpainting (edit specific areas)
  - Background removal
  - Object removal
- 💾 Export with metadata:
  - Include generation params
  - Watermark option

**Technical Implementation:**
```typescript
interface ImageDisplay {
  viewMode: 'thumbnail' | 'fullsize' | 'lightbox';
  downloadFormat: 'png' | 'jpg' | 'webp';
  editMode: boolean;
  cropPresets: string[];
  regenerationParams: {
    prompt: string;
    style: string;
    dimensions: { width: number; height: number };
  };
}
```

---

## Implementation Priority

### Phase 1: Core Functionality (Weeks 1-2)
**Goal:** Get all content types displaying properly with basic copy functionality

1. **Social Media Display** (2-3 days)
   - Platform-specific cards
   - Character counts
   - Hashtag highlighting
   - Copy buttons

2. **Blog Post Display** (2-3 days)
   - Rich text rendering
   - Table of contents
   - Reading time
   - Copy functionality

3. **Video Script Display** (2 days)
   - Scene breakdown
   - Duration tracking
   - Copy functionality

4. **Copy-to-Clipboard Enhancement** (1 day)
   - Add to all content types
   - Success notifications
   - Keyboard shortcuts (Ctrl+C)

### Phase 2: Enhanced Editing (Weeks 3-4)
**Goal:** Allow users to modify generated content

5. **Inline Editing Framework** (3 days)
   - Contenteditable components
   - Validation rules per content type
   - Auto-save
   - Undo/redo

6. **Email Sequence Enhancements** (2 days)
   - Timeline visualization
   - Reordering
   - HTML preview

7. **Ad Copy Enhancements** (2 days)
   - Platform previews
   - Compliance checking
   - A/B variant creator

8. **Blog Post Editor** (3 days)
   - Rich text toolbar
   - SEO panel
   - Markdown support

### Phase 3: Platform Previews (Weeks 5-6)
**Goal:** Show users how content will look on actual platforms

9. **Social Media Previews** (4 days)
   - Twitter/X card mockup
   - LinkedIn post mockup
   - Instagram preview
   - Facebook preview

10. **Ad Platform Previews** (3 days)
    - Google Ads preview
    - Facebook Ads preview
    - LinkedIn Ads preview

11. **Email Template Previews** (2 days)
    - HTML email renderer
    - Mobile/desktop views

### Phase 4: Export & Integration (Weeks 7-8)
**Goal:** Allow users to use content in their tools

12. **Export System** (5 days)
    - WordPress XML export
    - ESP CSV exports
    - Ad platform CSV/JSON exports
    - Social media scheduler formats

13. **Analytics Integration** (3 days)
    - View tracking
    - Copy tracking
    - Export tracking
    - Performance scoring

### Phase 5: Advanced Features (Weeks 9-10)
**Goal:** AI-powered content optimization

14. **Content Regeneration** (3 days)
    - Edit prompts and regenerate
    - Variation generator
    - Parameter tuning

15. **A/B Testing Tools** (3 days)
    - Create variants
    - Track performance
    - Winner selection

16. **Content Optimization** (4 days)
    - SEO scoring for blogs
    - Readability analysis
    - Engagement prediction
    - Improvement suggestions

---

## Technical Architecture

### Frontend Components Structure

```
src/components/content/
├── displays/
│   ├── EmailSequenceDisplay.tsx
│   ├── AdCopyDisplay.tsx (✅ implemented)
│   ├── BlogPostDisplay.tsx
│   ├── SocialMediaDisplay.tsx
│   ├── VideoScriptDisplay.tsx
│   └── ImageDisplay.tsx (✅ implemented)
├── editors/
│   ├── EmailEditor.tsx
│   ├── AdCopyEditor.tsx
│   ├── BlogPostEditor.tsx
│   ├── SocialMediaEditor.tsx
│   └── VideoScriptEditor.tsx
├── previews/
│   ├── GoogleAdsPreview.tsx
│   ├── FacebookAdsPreview.tsx
│   ├── TwitterPreview.tsx
│   ├── LinkedInPreview.tsx
│   ├── InstagramPreview.tsx
│   └── EmailPreview.tsx
├── exporters/
│   ├── WordPressExporter.tsx
│   ├── ESPExporter.tsx
│   ├── AdPlatformExporter.tsx
│   └── SocialMediaExporter.tsx
└── shared/
    ├── CopyButton.tsx
    ├── CharacterCounter.tsx
    ├── ComplianceIndicator.tsx
    └── EditableField.tsx
```

### Backend API Endpoints

```
Content Editing:
POST   /api/content/{content_id}/edit
PUT    /api/content/{content_id}/update
POST   /api/content/{content_id}/regenerate

Content Export:
GET    /api/content/{content_id}/export/{format}
POST   /api/content/bulk-export

Analytics:
POST   /api/content/{content_id}/track/view
POST   /api/content/{content_id}/track/copy
POST   /api/content/{content_id}/track/export

Validation:
POST   /api/content/validate/ad-copy
POST   /api/content/validate/social-post
POST   /api/content/validate/seo
```

### Database Schema Updates

```sql
-- Add content editing history
CREATE TABLE content_edits (
    id UUID PRIMARY KEY,
    content_id UUID REFERENCES generated_content(id),
    user_id UUID REFERENCES users(id),
    field_edited VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    edited_at TIMESTAMP DEFAULT NOW()
);

-- Add content tracking
CREATE TABLE content_analytics (
    id UUID PRIMARY KEY,
    content_id UUID REFERENCES generated_content(id),
    event_type VARCHAR(50), -- 'view', 'copy', 'export', 'edit'
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add export records
CREATE TABLE content_exports (
    id UUID PRIMARY KEY,
    content_id UUID REFERENCES generated_content(id),
    user_id UUID REFERENCES users(id),
    export_format VARCHAR(50),
    export_data JSONB,
    exported_at TIMESTAMP DEFAULT NOW()
);
```

---

## UI/UX Design Principles

### Consistency
- Use same color scheme across content types:
  - Blue: Headlines/Titles
  - Green: Descriptions/Body
  - Purple: Meta/Additional text
  - Orange: CTAs/Actions
  - Red: Warnings/Violations
  - Gray: Metadata/Secondary info

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation for all actions
- Screen reader friendly
- High contrast mode support
- Font size controls

### Performance
- Lazy load content previews
- Optimize image rendering
- Cache export formats
- Debounce inline editing

### Mobile Responsiveness
- Touch-friendly buttons (min 44x44px)
- Collapsible sections on mobile
- Swipe gestures for navigation
- Bottom sheet modals

---

## Success Metrics

### User Engagement
- Time spent viewing content
- Copy-to-clipboard usage
- Export frequency
- Edit/regeneration rate

### Content Quality
- User satisfaction ratings
- Regeneration frequency (lower = better)
- Export completion rate
- Platform compliance score

### Business Impact
- Reduced time to publish
- Increased content usage
- Higher user retention
- Feature adoption rate

---

## Risk Mitigation

### Technical Risks
1. **Performance**: Large content rendering
   - Solution: Virtual scrolling, pagination

2. **Data Loss**: Inline editing without save
   - Solution: Auto-save, version history

3. **Export Failures**: Platform API changes
   - Solution: Format validation, fallback options

### User Experience Risks
1. **Overwhelming UI**: Too many features
   - Solution: Progressive disclosure, onboarding

2. **Learning Curve**: Complex editing tools
   - Solution: Tooltips, tutorials, templates

3. **Platform Compatibility**: Export format issues
   - Solution: Format testing, user validation

---

## Future Enhancements (Beyond Phase 5)

### AI-Powered Features
- Content improvement suggestions
- Automated A/B test creation
- Performance prediction
- Personalization by audience segment

### Collaboration
- Team comments on content
- Approval workflows
- Version comparison
- Shared content library

### Integration
- Direct publishing to platforms
- CMS plugins (WordPress, Shopify)
- Social media auto-posting
- Email ESP integration

### Advanced Analytics
- Content performance dashboard
- ROI tracking per content piece
- Engagement heatmaps
- Competitor analysis

---

## Notes

- This plan assumes iterative development with user feedback between phases
- Priorities may shift based on user research and analytics
- Each phase includes time for testing and bug fixes
- API design should support future features (versioning, extensibility)
- Security considerations for content editing and export
- GDPR/privacy compliance for analytics tracking

---

**Document Version:** 1.0
**Last Updated:** 2025-10-08
**Author:** CampaignForge Development Team
**Status:** Planning Phase
