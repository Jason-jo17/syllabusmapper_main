-- 001_schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE colleges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  short_code TEXT UNIQUE NOT NULL,
  location TEXT,
  affiliation TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE syllabi (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  college_id UUID REFERENCES colleges(id) ON DELETE CASCADE,
  stream TEXT NOT NULL,
  regulation TEXT,
  title TEXT NOT NULL,
  source_type TEXT NOT NULL,    -- pdf|url|md|xlsx|docx|image
  source_url TEXT,
  storage_path TEXT,
  raw_text TEXT,
  structured_json JSONB,
  ingestion_status TEXT DEFAULT 'pending',
  ingestion_error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  syllabus_id UUID REFERENCES syllabi(id) ON DELETE CASCADE,
  college_id UUID REFERENCES colleges(id),
  course_code TEXT,
  course_title TEXT NOT NULL,
  stream TEXT,
  year_of_study INTEGER,      -- 1-4
  semester INTEGER,           -- 1-8
  semester_label TEXT,        -- e.g. "Sem 3", "Physics Cycle"
  credits INTEGER,
  course_type TEXT,           -- core|elective|lab|project
  topics JSONB,               -- array of module/topic strings
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE course_outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  co_code TEXT NOT NULL,      -- CO1, CO2, etc.
  description TEXT NOT NULL,
  bloom_level INTEGER,        -- 1-6
  bloom_verb TEXT,            -- Apply, Analyse, Design, etc.
  embedding VECTOR(1024),     -- voyage-3 uses 1024 dims
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE job_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_name TEXT NOT NULL,
  domain TEXT,
  category TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE skill_nodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_role_id UUID REFERENCES job_roles(id),
  level TEXT NOT NULL,          -- L0-L5
  level_num INTEGER NOT NULL,   -- 0-5
  common_tag TEXT,
  domain TEXT,
  category TEXT,
  knowledge_set TEXT NOT NULL,
  concept TEXT NOT NULL,        -- What to KNOW
  skill_description TEXT NOT NULL, -- What to DO
  bloom_level INTEGER,
  task_type TEXT,               -- Concept|Task
  tools TEXT,
  year_label TEXT,
  role_proximity TEXT,
  embedding VECTOR(1024),
  -- Pre-mapped CO references (for ECE VTU data)
  co_primary_text TEXT,
  co_primary_course TEXT,
  co_primary_year TEXT,
  co_primary_sem TEXT,
  co_secondary_text TEXT,
  co_secondary_course TEXT,
  co_secondary_year TEXT,
  co_secondary_sem TEXT,
  co_tertiary_text TEXT,
  co_tertiary_course TEXT,
  co_tertiary_year TEXT,
  co_tertiary_sem TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE co_skill_mappings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  syllabus_id UUID REFERENCES syllabi(id),
  course_id UUID REFERENCES courses(id),
  co_id UUID REFERENCES course_outcomes(id),
  skill_node_id UUID REFERENCES skill_nodes(id),
  similarity_score FLOAT NOT NULL,
  match_type TEXT,              -- direct|partial|prerequisite
  ai_justification TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(co_id, skill_node_id)
);

CREATE TABLE gap_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  syllabus_id UUID REFERENCES syllabi(id),
  job_role_id UUID REFERENCES job_roles(id),
  total_skills INTEGER,
  covered_skills INTEGER,
  coverage_pct FLOAT,
  gaps JSONB,
  priority_gaps JSONB,
  generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_co_emb ON course_outcomes USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);
CREATE INDEX idx_sk_emb ON skill_nodes USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);
CREATE INDEX idx_courses_syl ON courses(syllabus_id);
CREATE INDEX idx_courses_col_str ON courses(college_id, stream, semester);
CREATE INDEX idx_maps_syl ON co_skill_mappings(syllabus_id);
