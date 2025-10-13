-- Link campaign to intelligence_core
UPDATE campaigns 
SET intelligence_id = '1cebca08-c988-43b7-b8ac-61a5f6498d1a'
WHERE id = '4b5e4dd2-1b6e-4b33-bb7c-8b3f9e51c8b8';

-- Verify the update
SELECT id, title, intelligence_id FROM campaigns WHERE id = '4b5e4dd2-1b6e-4b33-bb7c-8b3f9e51c8b8';
