-- src/media_generation/repository/schema.sql
CREATE TABLE media_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    salespage_url TEXT,
    media_type TEXT CHECK (media_type IN ('image','video')) NOT NULL,
    platform TEXT NOT NULL,               -- NEW COLUMN
    prompt TEXT NOT NULL,
    provider TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending','processing','complete','failed')) DEFAULT 'pending',
    output_url TEXT,
    cost_usd NUMERIC(10,4),              -- track API cost
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);