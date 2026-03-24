-- 002_vector_functions.sql
CREATE OR REPLACE FUNCTION match_skill_nodes(
  query_embedding VECTOR(1024),
  match_threshold FLOAT DEFAULT 0.62,
  match_count INT DEFAULT 20
) RETURNS TABLE(
  id UUID, level TEXT, level_num INTEGER, knowledge_set TEXT,
  concept TEXT, skill_description TEXT, job_role_id UUID,
  tools TEXT, task_type TEXT, bloom_level INTEGER, similarity FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT sn.id, sn.level, sn.level_num, sn.knowledge_set,
    sn.concept, sn.skill_description, sn.job_role_id,
    sn.tools, sn.task_type, sn.bloom_level,
    1 - (sn.embedding <=> query_embedding) AS similarity
  FROM skill_nodes sn
  WHERE 1 - (sn.embedding <=> query_embedding) > match_threshold
  ORDER BY sn.embedding <=> query_embedding
  LIMIT match_count;
END; $$;

CREATE OR REPLACE FUNCTION match_cos_in_syllabus(
  query_embedding VECTOR(1024),
  filter_syllabus_id UUID,
  match_threshold FLOAT DEFAULT 0.58,
  match_count INT DEFAULT 10
) RETURNS TABLE(
  co_id UUID, course_id UUID, co_code TEXT, description TEXT,
  course_title TEXT, semester INTEGER, semester_label TEXT,
  year_of_study INTEGER, bloom_level INTEGER, similarity FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT co.id, co.course_id, co.co_code, co.description,
    c.course_title, c.semester, c.semester_label, c.year_of_study,
    co.bloom_level,
    1 - (co.embedding <=> query_embedding) AS similarity
  FROM course_outcomes co
  JOIN courses c ON co.course_id = c.id
  WHERE c.syllabus_id = filter_syllabus_id
    AND 1 - (co.embedding <=> query_embedding) > match_threshold
  ORDER BY co.embedding <=> query_embedding
  LIMIT match_count;
END; $$;
