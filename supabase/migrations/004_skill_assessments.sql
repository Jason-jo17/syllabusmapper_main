-- Skill Assessments Table
CREATE TABLE IF NOT EXISTS skill_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_node_id UUID REFERENCES skill_nodes(id) ON DELETE CASCADE,
    domain TEXT,           -- Denormalized for easier lookups
    knowledge_set TEXT,    -- Denormalized
    skill_knowledge TEXT, -- Denormalized
    mcqs JSONB DEFAULT '[]'::jsonb,
    subjective_tasks JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for searching by skill node
CREATE INDEX IF NOT EXISTS idx_skill_assessments_node ON skill_assessments(skill_node_id);
CREATE INDEX IF NOT EXISTS idx_skill_assessments_lookup ON skill_assessments(domain, knowledge_set);

-- Enable RLS
ALTER TABLE skill_assessments ENABLE ROW LEVEL SECURITY;

-- Allow public read access (for now)
CREATE POLICY "Allow public read access for skill_assessments"
ON skill_assessments FOR SELECT
TO anon, authenticated
USING (true);
