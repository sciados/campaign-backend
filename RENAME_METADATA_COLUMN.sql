-- Migration: Rename metadata column to extra_metadata in scraped_images table
-- Reason: 'metadata' is a reserved keyword in SQLAlchemy Declarative API
-- Date: 2025-10-15

-- Rename the column
ALTER TABLE scraped_images
RENAME COLUMN metadata TO extra_metadata;

-- Verify the change
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'scraped_images'
  AND column_name = 'extra_metadata';

-- Should return: extra_metadata | jsonb
