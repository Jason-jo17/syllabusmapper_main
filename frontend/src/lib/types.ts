export interface SkillNode {
  id: string;
  level: string;
  knowledge_set: string;
  concept: string;
  skill_description: string;
  task_type?: string;
  tools?: string;
  bloom_level?: number;
  co_primary_text?: string;
  co_primary_course?: string;
  co_primary_year?: string;
  co_primary_sem?: string;
  co_secondary_text?: string;
  co_secondary_course?: string;
  co_secondary_year?: string;
  co_secondary_sem?: string;
  co_tertiary_text?: string;
  co_tertiary_course?: string;
  co_tertiary_year?: string;
  co_tertiary_sem?: string;
}

export interface Course {
  id: string;
  course_code: string;
  course_title: string;
  year_of_study?: number;
  semester?: number;
  semester_label?: string;
  co_count?: number;
  skill_count?: number;
}

export interface CourseOutcome {
  id: string;
  co_code: string;
  description: string;
  bloom_level?: number;
  bloom_verb?: string;
}

export interface SkillAddressed {
  knowledge_set: string;
  skill_knowledge: string;
  bl_level: string;
}

export interface Event {
  id: string;
  event_name: string;
  organizing_body: string;
  description: string;
  problem_statement?: string;
  location?: string;
  mode?: string;
  knowledge_domain_1?: string;
  knowledge_domain_2?: string;
  event_type?: string;
  skills_addressed?: SkillAddressed[];
}
