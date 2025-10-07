-- Check all VARCHAR column lengths in generated_prompts table
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'generated_prompts'
    AND table_schema = 'public'
    AND data_type LIKE '%character%'
ORDER BY ordinal_position;
