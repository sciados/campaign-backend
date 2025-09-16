# Legacy Generator Deprecation Analysis

This document identifies intelligence generator files that have been superseded by the new modular content generation system.

## Analysis Summary

The new modular architecture has moved content generation from `src/intelligence/generators/` to `src/content/generators/` and `src/content/services/`. This analysis identifies which legacy files can be deprecated.

## Files Still in Use (DO NOT DEPRECATE)

These intelligence generator files are still actively used and should be retained:

### Core Infrastructure
- `src/intelligence/generators/base_generator.py` - Base class used by active generators
- `src/intelligence/generators/factory.py` - Factory pattern used by intelligence_content_service.py
- `src/intelligence/generators/__init__.py` - Module initialization

### Active Image/Video Generation
- `src/intelligence/generators/image_generator.py` - Used by media_service.py for image generation
- `src/intelligence/generators/stability_ai_generator.py` - Stability AI integration
- `src/intelligence/generators/slideshow_video_generator.py` - Used by media_service.py (commented out but kept for Railway deployment)

### Email Subject Line Services
- `src/intelligence/generators/subject_line_ai_service.py` - Used by email_generator.py
- `src/intelligence/generators/self_learning_subject_service.py` - Used by email_generator.py

### Configuration and Monitoring
- `src/intelligence/generators/config/manager.py` - Configuration management
- `src/intelligence/generators/monitoring/health_monitor.py` - System health monitoring

## Files That Can Be Deprecated

These files have been superseded by the new content module:

### Content Generation (Superseded by src/content/generators/)
```bash
# DEPRECATED: Superseded by src/content/generators/ad_copy_generator.py
src/intelligence/generators/ad_copy_generator.py

# DEPRECATED: Superseded by src/content/generators/blog_content_generator.py
src/intelligence/generators/blog_post_generator.py

# DEPRECATED: Superseded by src/content/generators/email_generator.py
src/intelligence/generators/email_generator.py

# DEPRECATED: Superseded by src/content/generators/social_media_generator.py
src/intelligence/generators/social_media_generator.py

# DEPRECATED: No longer used in new architecture
src/intelligence/generators/campaign_angle_generator.py

# DEPRECATED: Superseded by content module video services
src/intelligence/generators/video_script_generator.py
```

### Database and Utilities (Legacy)
```bash
# DEPRECATED: Database seeding moved to core module
src/intelligence/generators/database_seeder.py
```

### Landing Page Generation (Large Legacy System)
```bash
# DEPRECATED: Entire landing page generation system superseded
src/intelligence/generators/landing_page/
├── analytics/
├── components/
├── core/
├── database/
├── intelligence/
├── routes.py
├── templates/
├── utils/
├── variants/
└── __init__.py
```

## Deprecation Strategy

### Phase 1: Mark as Deprecated (Immediate)
1. Add deprecation warnings to superseded files
2. Update docstrings to indicate replacement modules
3. Add comments pointing to new implementations

### Phase 2: Remove Imports (After Testing)
1. Ensure no active code imports deprecated generators
2. Update any remaining references to use content module
3. Test all content generation functionality

### Phase 3: Archive Files (Future Release)
1. Move deprecated files to `archive/` directory
2. Keep for historical reference and rollback if needed
3. Remove from active codebase

## Implementation Steps

### Step 1: Add Deprecation Warnings

Add this header to each deprecated file:

```python
"""
DEPRECATED: This file has been superseded by the new modular content generation system.

New Implementation: src/content/generators/{equivalent_file}.py
Deprecation Date: 2024-09-16
Planned Removal: Next major release

This file is maintained for compatibility but will be removed in future versions.
Use the new content module for all content generation tasks.
"""

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use src.content.generators instead.",
    DeprecationWarning,
    stacklevel=2
)
```

### Step 2: Update Import References

Replace any remaining imports:

```python
# OLD (deprecated)
from src.intelligence.generators.ad_copy_generator import AdCopyGenerator

# NEW (use instead)
from src.content.generators.ad_copy_generator import AdCopyGenerator
```

### Step 3: Verify Content Module Coverage

Ensure the content module provides equivalent functionality for:
- ✅ Ad copy generation
- ✅ Blog content generation
- ✅ Email sequence generation
- ✅ Social media content generation
- ❓ Campaign angle generation (verify replacement)
- ❓ Video script generation (verify replacement)

## Files to Keep Active

These intelligence generator files should remain active:

1. **Image Generation**: `image_generator.py`, `stability_ai_generator.py`
2. **Base Infrastructure**: `base_generator.py`, `factory.py`, `__init__.py`
3. **Email Services**: `subject_line_ai_service.py`, `self_learning_subject_service.py`
4. **Configuration**: `config/manager.py`
5. **Monitoring**: `monitoring/health_monitor.py`
6. **Video Generation**: `slideshow_video_generator.py` (disabled but kept for Railway)

## Testing Requirements

Before removing deprecated files:

1. ✅ Verify all content generation routes work with content module
2. ✅ Test email generation with new EmailGenerator
3. ✅ Test social media generation with new SocialMediaGenerator
4. ✅ Test ad copy generation with new AdCopyGenerator
5. ✅ Test blog content generation with new BlogContentGenerator
6. ❓ Verify no 500 errors in production deployment
7. ❓ Confirm all legacy import paths are updated

## Backup Strategy

Before deprecation:
1. Create git branch with all legacy files intact
2. Tag current state as "pre-deprecation-backup"
3. Document rollback procedures if needed

This ensures we can restore functionality if issues arise during transition.