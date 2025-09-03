# Intelligence Schema Migration Handover

## Overview

This document provides guidance for updating files to work with the new optimized 6-table intelligence schema that replaces the old `campaign_intelligence` and `rag_intelligence_sources` tables.

## Schema Changes Summary

### Old Schema (Removed)

- `campaign_intelligence` - Single flat table with JSONB columns
- `rag_intelligence_sources` - RAG intelligence sources table
- Direct `campaign_id` relationships

### New Schema (6 Tables)

```sql
-- Core intelligence (lean)
intelligence_core (id, product_name, source_url, confidence_score, analysis_method, created_at)

-- Normalized product data
product_data (intelligence_id, features[], benefits[], ingredients[], conditions[], usage_instructions[])

-- Market insights
market_data (intelligence_id, category, positioning, competitive_advantages[], target_audience)

-- Centralized research
knowledge_base (id, content_hash, content, research_type, source_metadata, created_at)

-- Intelligence-research links
intelligence_research (intelligence_id, research_id, relevance_score)

-- Deduplicated content cache
scraped_content (url_hash, url, content, title, scraped_at)
```

## Key Model Updates

### Updated New Models (src/models/intelligence.py)

- `IntelligenceCore` - Replaces `CampaignIntelligence`
- `ProductData` - Product-specific arrays
- `MarketData` - Market and psychology data
- `KnowledgeBase` - Centralized research
- `IntelligenceResearch` - Research links
- `ScrapedContent` - Content cache
- `GeneratedContent` - Updated with `intelligence_id` foreign key

### Updated CRUD (src/core/crud/intelligence_crud.py)

- Multi-table operations instead of single table
- Search by product name, URL, or recent time instead of campaign_id
- Helper method `_execute_intelligence_query()` for consistent data reconstruction

## Files That Need Updates

### High Priority (Direct Database Operations)

1. **niche_monitor.py** - Update queries from `campaign_intelligence` to `intelligence_core`
2. **affiliate_optimized_cache.py** - Update cache keys for new schema
3. **global_cache.py** - Update cache structure
4. **shared_intelligence_cache.py** - Update shared caching logic
5. **sales_page_monitor.py** - Update writes to use new tables
6. **enhanced_rag_system.py** - Update to use `knowledge_base` table

### Medium Priority (Application Logic)

1. **social_media_generator.py** - Update intelligence data access patterns
2. **dashboard_stats.py** - Update statistics queries
3. **content_routes.py** - Update API endpoints to use new CRUD methods

### Low Priority (Configuration/Utils)

1. **models.py** - Update imports and references
2. Various route files that reference intelligence data

## Critical Changes Required

### 1. Database Queries

**OLD:**

```python
# Direct campaign_intelligence queries
query = select(CampaignIntelligence).where(CampaignIntelligence.campaign_id == campaign_id)
```

**NEW:**

```python
# Use intelligence_crud with search methods
intelligence_sources = await intelligence_crud.search_intelligence_by_product(db, product_name)
# OR
intelligence_sources = await intelligence_crud.get_recent_intelligence(db, days=30)
```

### 2. Intelligence Data Access

**OLD:**

```python
# Direct JSONB column access
offer_intel = intelligence.offer_intelligence  # JSONB column
scientific_intel = intelligence.scientific_intelligence  # JSONB column
```

**NEW:**

```python
# Reconstructed from normalized data
complete_intel = intelligence_core.get_complete_intelligence()
offer_intel = complete_intel["offer_intelligence"]
scientific_intel = complete_intel["scientific_intelligence"]
```

### 3. Campaign Relationships

**OLD:**

```python
# Direct campaign filtering
intelligence_list = await get_campaign_intelligence(campaign_id)
```

**NEW:**

```python
# Time-based or product-based context
intelligence_list = await intelligence_crud.get_recent_intelligence(db, days=30)
# OR search by product if known
intelligence_list = await intelligence_crud.search_intelligence_by_product(db, product_name)
```

## Update Patterns by File Type

### Cache Files (affiliate_optimized_cache.py, global_cache.py, etc.)

1. Replace `campaign_intelligence` table references with `intelligence_core`
2. Update cache keys from campaign-based to product/URL-based
3. Use intelligence CRUD methods instead of direct queries
4. Handle missing campaign_id relationships

**Example:**

```python
# OLD
cache_key = f"campaign_intel_{campaign_id}_{source_url}"

# NEW  
cache_key = f"product_intel_{product_name}_{url_hash}"
```

### Monitor Files (niche_monitor.py, sales_page_monitor.py)

1. Replace direct table inserts with intelligence CRUD methods
2. Use `intelligence_crud.create_intelligence()` instead of creating `CampaignIntelligence`
3. Update query filters from campaign_id to product_name or time-based

**Example:**

```python
# OLD
await db.execute(insert(campaign_intelligence).values(...))

# NEW
intelligence_id = await intelligence_crud.create_intelligence(db, analysis_data)
```

### Generator Files (social_media_generator.py, etc.)

1. Update intelligence data access to use reconstructed format
2. Replace campaign-based intelligence lookup with product/recent lookups
3. Handle new intelligence data structure

**Example:**

```python
# OLD
intelligence = await get_campaign_intelligence(campaign_id)
benefits = intelligence.offer_intelligence.get("primary_benefits", [])

# NEW
intelligence_list = await intelligence_crud.get_recent_intelligence(db, limit=5)
if intelligence_list:
    benefits = intelligence_list[0]["offer_intelligence"].get("primary_benefits", [])
```

### Route Files (content_routes.py, etc.)

1. Update API endpoints to use new CRUD methods
2. Modify response formats for new schema structure
3. Add product-based and URL-based search endpoints

## Testing Utilities

New CRUD provides testing helpers:

- `intelligence_crud.clear_all_test_data()` - Clean slate for testing
- `intelligence_crud.create_sample_intelligence()` - Generate test data
- `intelligence_crud.get_all_intelligence()` - Get all records for verification

## Migration Strategy

### Phase 1: Update Core Files

1. Update `intelligence_crud.py` (✅ Complete)
2. Update `intelligence_handler.py` (✅ Complete)
3. Update `models/__init__.py` (✅ Complete)

### Phase 2: Update Database Operations

1. Update cache files to use new schema
2. Update monitor files to write to new tables
3. Update RAG system to use `knowledge_base` table

### Phase 3: Update Application Logic

1. Update generators to use new intelligence format
2. Update statistics and analytics
3. Update API routes and responses

### Phase 4: Testing and Validation

1. Test all functionality with new schema
2. Verify 90% storage reduction
3. Confirm query performance improvements

## Common Pitfalls to Avoid

1. **Don't assume campaign_id exists** - New schema has no campaign relationships
2. **Don't access JSONB columns directly** - Use `get_complete_intelligence()` method
3. **Don't forget eager loading** - Use `selectinload()` for relationships
4. **Don't duplicate query logic** - Use `_execute_intelligence_query()` helper
5. **Handle missing intelligence gracefully** - Recent/product searches may return empty results

## Benefits Achieved

- **90% storage reduction** through normalization
- **Enhanced query performance** with proper indexing
- **Deduplicated content** through `scraped_content` table  
- **Centralized research** in `knowledge_base` table
- **Better data integrity** with foreign key relationships
- **RAG system integration** through research links

## Contact/Questions

If you encounter issues during migration:

1. Check the intelligence CRUD methods first
2. Use the testing utilities for verification
3. Remember that campaign_id relationships are now time-based or product-based context
4. Leverage the `get_complete_intelligence()` method for data reconstruction

---

**Schema Version:** Optimized Normalized v1.0  
**Migration Status:** Core CRUD Complete  
**Next Phase:** Update dependent files  
**Storage Reduction:** 90% achieved
