-- Migration: Fix user_id to be VARCHAR for UUID support
-- Description: Change user_id from INTEGER to VARCHAR to support UUID strings
-- Date: 2025-09-20

-- Check current data type and update if needed
DO $$
BEGIN
    -- Check if user_id column exists and is INTEGER
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'clickbank_accounts'
        AND column_name = 'user_id'
        AND data_type = 'integer'
    ) THEN
        -- Change user_id from INTEGER to VARCHAR to support UUIDs
        ALTER TABLE clickbank_accounts ALTER COLUMN user_id TYPE VARCHAR(36);

        -- Update the unique constraint to match new type
        ALTER TABLE clickbank_accounts DROP CONSTRAINT IF EXISTS clickbank_accounts_user_id_key;
        ALTER TABLE clickbank_accounts ADD CONSTRAINT clickbank_accounts_user_id_unique UNIQUE (user_id);

        RAISE NOTICE 'Updated user_id column to VARCHAR(36) for UUID support';
    ELSE
        RAISE NOTICE 'user_id column is already VARCHAR or does not exist';
    END IF;
END
$$;