-- Fix ai_model column length - needs to store full model names like "deepseek-chat (DeepSeek V3)"
-- Current: VARCHAR(20) is too short
-- Should be: VARCHAR(100) to match model definition

ALTER TABLE generated_prompts
    ALTER COLUMN ai_model TYPE VARCHAR(100);

-- Also verify ai_provider is adequate (should be VARCHAR(50))
ALTER TABLE generated_prompts
    ALTER COLUMN ai_provider TYPE VARCHAR(50);
