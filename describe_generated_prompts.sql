-- Get complete schema of generated_prompts table including column types and constraints
SELECT
    column_name,
    data_type,
    character_maximum_length,
    numeric_precision,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'generated_prompts'
    AND table_schema = 'public'
ORDER BY ordinal_position;
