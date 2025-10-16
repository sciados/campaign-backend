-- Migration: Add salespage_url column to campaigns table
-- This makes it easier to access the sales page URL without querying intelligence data
-- Date: 2025-10-15

-- Add the column
ALTER TABLE campaigns
ADD COLUMN salespage_url VARCHAR(1000) NULL;

-- Optional: Update existing campaigns with intelligence data
-- UPDATE campaigns c
-- SET salespage_url = ic.salespage_url
-- FROM intelligence_core ic
-- WHERE c.intelligence_id = ic.id
--   AND c.salespage_url IS NULL;

-- Verify the column was added
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'campaigns'
  AND column_name = 'salespage_url';
