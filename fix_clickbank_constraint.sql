-- Fix clickbank_accounts unique constraint
-- The ON CONFLICT clause requires a unique constraint on user_id

-- Check current table structure
SELECT
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name = 'clickbank_accounts';

-- Add unique constraint on user_id if it doesn't exist
DO $$
BEGIN
    -- Check if unique constraint exists on user_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'clickbank_accounts'
        AND tc.constraint_type = 'UNIQUE'
        AND kcu.column_name = 'user_id'
    ) THEN
        -- Add unique constraint on user_id
        ALTER TABLE clickbank_accounts ADD CONSTRAINT clickbank_accounts_user_id_unique UNIQUE (user_id);
        RAISE NOTICE 'Added unique constraint on user_id column';
    ELSE
        RAISE NOTICE 'Unique constraint on user_id already exists';
    END IF;
END
$$;