import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Target, LayoutGrid, Calendar } from "lucide-react";
import type { Course, CourseOutcome, SkillNode, Event, SkillAddressed } from "@/lib/types";

interface Props {
  course: Course | null;
  cos: CourseOutcome[];          // All COs for this course
  mappedSkills: SkillNode[];     // Skills mapped TO this course
  allEvents?: Event[];             // All events fetched
  onClose: () => void;
}

const LEVEL_COLORS = {
  L0:'#f59e0b', L1:'#3b82f6', L2:'#22c55e',
  L3:'#a855f7', L4:'#f43f5e', L5:'#06b6d4'
};

export function DetailPanel({ course, cos, mappedSkills, allEvents = [], onClose }: Props) {
  const [activeTab, setActiveTab] = useState<'cos'|'skills'|'events'>('skills');
  if (!course) return null;
  
  // Which CO codes are hit by mapped skills?
  const hitCOCodes = new Set<string>();
  mappedSkills.forEach(sk => {
    // skill.co_primary_course === course.title → extract CO code
    if (sk.co_primary_course === course.course_title) {
      const m = sk.co_primary_text?.match(/CO\d+/g);
      m?.forEach(c => hitCOCodes.add(c));
    }
    if (sk.co_secondary_course === course.course_title) {
      const m = sk.co_secondary_text?.match(/CO\d+/g);
      m?.forEach(c => hitCOCodes.add(c));
    }
    if (sk.co_tertiary_course === course.course_title) {
      const m = sk.co_tertiary_text?.match(/CO\d+/g);
      m?.forEach(c => hitCOCodes.add(c));
    }
  });

  // Which events map to the skills in this course?
  const courseEvents = allEvents.filter(ev => {
    return ev.skills_addressed?.some((es: SkillAddressed) => 
      mappedSkills.some(sk => sk.concept && es.knowledge_set && sk.concept.toLowerCase().includes(es.knowledge_set.toLowerCase()))
    );
  });

  return (
    <AnimatePresence>
      <motion.div
        key="detail-panel"
        initial={{ x: 340, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 340, opacity: 0 }}
        transition={{ type: "spring", damping: 28, stiffness: 280 }}
        className="w-[340px] flex-shrink-0 bg-[var(--bg1)] border-l border-[var(--bd)] flex flex-col overflow-hidden fixed right-0 top-14 bottom-0 z-20 shadow-2xl transition-colors duration-200"
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-[var(--bd)] relative flex-shrink-0">
          <button onClick={onClose} className="absolute top-3 right-3 text-[var(--tx3)] hover:text-[var(--tx)] transition-colors">
            <X size={16} />
          </button>
          <div className="text-[10px] font-mono text-[var(--tx3)] mb-1">{course.course_code}</div>
          <div className="text-[13px] font-bold text-[var(--tx)] pr-6">{course.course_title}</div>
          <div className="text-[10px] font-mono text-[var(--acc)] mt-1">
            {course.year_of_study ? `Year ${course.year_of_study}` : ''} {course.semester_label ? `· ${course.semester_label}` : ''}
          </div>
          <div className="text-[10px] text-[var(--tx3)] mt-1 flex gap-2">
            <span>{mappedSkills.length} Skills</span>·<span>{cos.length} COs</span>·<span>{courseEvents.length} Events</span>
          </div>
        </div>

        {/* Tabs container */}
        <div className="flex border-b border-[var(--bd)] bg-[var(--bg1)] px-2">
          <button 
            onClick={() => setActiveTab('cos')} 
            className={`flex items-center gap-1.5 px-3 py-2 text-[11px] font-medium border-b-2 transition-colors ${activeTab === 'cos' ? 'border-[var(--acc)] text-[var(--acc)]' : 'border-transparent text-[var(--tx3)] hover:text-[var(--tx2)]'}`}
          >
            <Target size={14} /> Outcomes
          </button>
          <button 
            onClick={() => setActiveTab('skills')} 
            className={`flex items-center gap-1.5 px-3 py-2 text-[11px] font-medium border-b-2 transition-colors ${activeTab === 'skills' ? 'border-[var(--acc)] text-[var(--acc)]' : 'border-transparent text-[var(--tx3)] hover:text-[var(--tx2)]'}`}
          >
            <LayoutGrid size={14} /> Skills
          </button>
          <button 
            onClick={() => setActiveTab('events')} 
            className={`flex items-center gap-1.5 px-3 py-2 text-[11px] font-medium border-b-2 transition-colors ${activeTab === 'events' ? 'border-[var(--acc)] text-[var(--acc)]' : 'border-transparent text-[var(--tx3)] hover:text-[var(--tx2)]'}`}
          >
            <Calendar size={14} /> Events
            {courseEvents.length > 0 && (
              <span className="ml-1 bg-[var(--acc)] text-white text-[9px] px-1.5 rounded-full">{courseEvents.length}</span>
            )}
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-3 bg-[var(--bg)]/30">
          
          {/* COs Tab */}
          {activeTab === 'cos' && (
            <div>
              <div className="text-[10px] font-mono text-[var(--tx3)] uppercase tracking-widest mb-2 flex items-center gap-2">
                Course Outcomes
                {hitCOCodes.size > 0 && <span className="text-[#22c55e]">● {hitCOCodes.size} linked</span>}
              </div>
              <div className="space-y-2 mb-4">
                {cos.length === 0 && <div className="text-[11px] text-[var(--tx4)] text-center py-4">No COs found</div>}
                {cos.map(co => {
                  const isHit = hitCOCodes.has(co.co_code);
                  return (
                    <div key={co.id}
                      className={`rounded-lg border p-2.5 transition-colors ${isHit
                        ? 'border-[var(--acc)] bg-[var(--glow)] shadow-sm'
                        : 'border-[var(--bd)] bg-[var(--bg1)]'}`}
                    >
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-[var(--bg3)] text-[var(--acc)]">
                          {co.co_code}
                        </span>
                        {co.bloom_level && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-[var(--bg3)] text-[var(--tx3)] font-mono">
                            BL{co.bloom_level}
                          </span>
                        )}
                        {isHit && <span className="text-[9px] font-mono text-[#22c55e]">● mapped</span>}
                      </div>
                      <div className="text-[11px] text-[var(--tx2)] leading-relaxed">
                        {co.description}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Mapped Skills Tab */}
          {activeTab === 'skills' && (
            <div>
              <div className="text-[10px] font-mono text-[var(--tx3)] uppercase tracking-widest mb-2">
                L0–L5 Skills Linked ({mappedSkills.length})
              </div>
              {mappedSkills.length === 0 ? (
                <div className="text-center py-8 text-[var(--tx4)] text-[11px]">
                  No skills mapped to this course yet.<br/>
                  <span className="text-[9px]">Potential curriculum gap or unlinked elective</span>
                </div>
              ) : (
                <div className="space-y-2">
                  {mappedSkills.map((sk, i) => {
                    const lc = LEVEL_COLORS[sk.level as keyof typeof LEVEL_COLORS] || '#6366f1';
                    return (
                      <div key={i} className="flex gap-2 p-2 rounded-lg bg-[var(--bg1)] border border-[var(--bd)] shadow-sm">
                        <span className="text-[9px] font-mono font-bold px-1.5 py-1 rounded flex-shrink-0 mt-0.5"
                          style={{ background: lc + '22', color: lc }}>{sk.level}</span>
                        <div className="flex-1 min-w-0">
                          <div className="text-[11px] text-[var(--tx)] leading-tight mb-1">{sk.concept}</div>
                          <div className="text-[9px] text-[var(--tx3)] font-mono">{sk.knowledge_set} · BL{sk.bloom_level} · {sk.task_type}</div>
                          {sk.tools && sk.tools !== '-' && (
                            <div className="text-[9px] text-[var(--tx3)] mt-0.5">🔧 {sk.tools.substring(0, 60)}</div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Events Tab */}
          {activeTab === 'events' && (
            <div>
              <div className="text-[10px] font-mono text-[var(--tx3)] uppercase tracking-widest mb-2">
                Related Events ({courseEvents.length})
              </div>
              {courseEvents.length === 0 ? (
                <div className="text-center py-8 text-[var(--tx4)] text-[11px]">
                  No events mapped to the skills in this course.<br/>
                </div>
              ) : (
                <div className="space-y-3">
                  {courseEvents.map((ev, i) => (
                    <div key={i} className="border border-[var(--bd)] bg-[var(--bg1)] rounded-lg p-3">
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-[9px] font-medium px-1.5 py-0.5 rounded bg-[rgba(99,102,241,0.1)] text-[var(--acc2)] border border-[rgba(99,102,241,0.2)]">
                          {ev.event_type || 'Event'}
                        </span>
                      </div>
                      <h4 className="text-[11px] font-bold text-[var(--tx)] leading-tight mb-1">{ev.event_name}</h4>
                      <p className="text-[9px] text-[var(--tx3)] mb-2 line-clamp-1">{ev.organizing_body}</p>
                      <div className="text-[9px] text-[var(--tx2)] font-mono bg-[var(--bg3)] p-1.5 rounded border border-[var(--bd)]">
                        Domain: {ev.knowledge_domain_1}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>
      </motion.div>
    </AnimatePresence>
  );
}
