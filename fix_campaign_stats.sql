-- Fix Campaign Stats for Generated Content
-- This script updates the campaign counters to reflect actual stored content

-- Update generated_content_count for campaign a6566fe3-7183-4c7a-a98e-dd2787a05cf5
UPDATE campaigns
SET generated_content_count = (
    SELECT COUNT(*)
    FROM generated_content
    WHERE campaign_id = 'a6566fe3-7183-4c7a-a98e-dd2787a05cf5'
),
updated_at = NOW()
WHERE id = 'a6566fe3-7183-4c7a-a98e-dd2787a05cf5';

-- Verify the update
SELECT
    id,
    name,
    intelligence_count,
    generated_content_count,
    sources_count,
    status,
    updated_at
FROM campaigns
WHERE id = 'a6566fe3-7183-4c7a-a98e-dd2787a05cf5';

-- Also check what content we have
SELECT
    id,
    content_type,
    content_title,
    created_at
FROM generated_content
WHERE campaign_id = 'a6566fe3-7183-4c7a-a98e-dd2787a05cf5';