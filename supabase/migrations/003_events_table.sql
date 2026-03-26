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

-- Disable RLS to ensure seeding script can run regardless of the key used
ALTER TABLE events DISABLE ROW LEVEL SECURITY;

-- Grant all permissions to all roles (for local seeding convenience)
GRANT ALL ON TABLE events TO anon, authenticated, service_role;
