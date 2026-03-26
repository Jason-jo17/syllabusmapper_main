-- 003_events_table.sql
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_name TEXT NOT NULL,
  organizing_body TEXT,
  description TEXT,
  problem_statement TEXT,
  registration_links TEXT,
  keywords TEXT,
  event_registration_deadline TEXT,
  event_date TEXT,
  location TEXT,
  mode TEXT,
  knowledge_domain_1 TEXT,
  knowledge_domain_2 TEXT,
  knowledge_domain_3 TEXT,
  event_type TEXT,
  emi_score TEXT,
  skills_addressed JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Clean up existing policies to avoid name conflicts
DROP POLICY IF EXISTS "Allow public read-only access" ON events;
DROP POLICY IF EXISTS "Allow authenticated full access" ON events;

-- Policies
CREATE POLICY "Allow public read-only access" ON events FOR SELECT USING (true);

-- Allow service role (and authenticated users seeding via service role key) to manage data
CREATE POLICY "Allow authenticated full access" ON events FOR ALL 
USING (auth.role() = 'service_role') 
WITH CHECK (auth.role() = 'service_role');
