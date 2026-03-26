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

-- Enable RLS (Optional, but good practice)
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read-only access" ON events FOR SELECT USING (true);
