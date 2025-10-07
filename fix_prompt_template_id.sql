-- Fix prompt_template_id - should be VARCHAR not UUID
-- This stores template names like 'email_sequence_solution_reveal', not UUIDs

ALTER TABLE generated_prompts
    ALTER COLUMN prompt_template_id TYPE VARCHAR;
