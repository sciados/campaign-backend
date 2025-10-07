-- Fix generation_time and generation_cost VARCHAR(20) constraints
-- These store decimal numbers as strings and can exceed 20 chars
-- Example: "1.2345678901234567890" or "0.00012345678901234567890"

ALTER TABLE generated_prompts
    ALTER COLUMN generation_time TYPE VARCHAR(50);

ALTER TABLE generated_prompts
    ALTER COLUMN generation_cost TYPE VARCHAR(50);
