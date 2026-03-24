"use client";
import type { Course, SkillNode } from "@/lib/types";

interface Props {
  course: Course;
  mappedSkills: SkillNode[];    // Skills for THIS course under current track filter
  allSkills: SkillNode[];       // All skills for this course regardless of filter
  coverageType: 'direct'|'partial'|'prereq'|'none';
  isSelected: boolean;
  trackFilter: 'none'|'ece'|'l0l1'|'l2l3'|'l4l5';
  onClick: () => void;
}

const LEVEL_COLORS = {
  L0:'#f59e0b',L1:'#3b82f6',L2:'#22c55e',L3:'#a855f7',L4:'#f43f5e',L5:'#06b6d4'
};
const COV_STYLES = {
  direct: { border: '#22c55e', bg: 'rgba(34,197,94,0.08)' },
  partial: { border: '#f59e0b', bg: 'rgba(245,158,11,0.08)' },
  prereq: { border: '#3b82f6', bg: 'rgba(59,130,246,0.08)' },
  none: { border: 'var(--bd)', bg: 'var(--bg1)' },
};

export function CourseCard({ course, mappedSkills, allSkills, coverageType, isSelected, trackFilter, onClick }: Props) {
  const levels = Array.from(new Set(mappedSkills.map(s => s.level)));
  const style = COV_STYLES[coverageType] || COV_STYLES.none;
  
  return (
    <div
      onClick={onClick}
      className="rounded-lg p-2.5 mb-2 cursor-pointer transition-all duration-150 relative border"
      style={{
        borderColor: isSelected ? 'var(--acc)' : style.border,
        backgroundColor: style.bg,
        boxShadow: isSelected ? '0 0 0 2px var(--acc), 0 0 0 4px var(--glow)' : undefined,
      }}
    >
      {/* Code */}
      <div className="text-[9px] font-mono text-[var(--tx3)] mb-0.5">{course.course_code}</div>
      
      {/* Title */}
      <div className="text-[11px] font-semibold text-[var(--tx)] leading-tight mb-1.5 min-h-[26px]">
        {course.course_title?.length > 36 ? course.course_title.substring(0,34)+'…' : course.course_title}
      </div>
      
      {/* Level chips */}
      {levels.length > 0 && (
        <div className="flex gap-1 flex-wrap mb-1.5">
          {levels.map(l => (
            <span key={l} className="text-[9px] font-mono font-bold px-1 py-0.5 rounded"
              style={{ background: (LEVEL_COLORS[l as keyof typeof LEVEL_COLORS]||'#6366f1')+'22',
                       color: LEVEL_COLORS[l as keyof typeof LEVEL_COLORS]||'#6366f1' }}>
              {l}
            </span>
          ))}
        </div>
      )}
      
      {/* Skill previews when track filter active */}
      {trackFilter !== 'none' && mappedSkills.length > 0 && (
        <div className="mb-1.5 space-y-0.5">
          {mappedSkills.slice(0,2).map((sk,i) => (
            <div key={i} className="flex gap-1.5 text-[9px] px-1.5 py-1 rounded bg-[var(--bg2)]/40">
              <span className="font-mono font-bold flex-shrink-0"
                style={{ color: LEVEL_COLORS[sk.level as keyof typeof LEVEL_COLORS]||'#6366f1' }}>
                {sk.level}
              </span>
              <span className="text-[var(--tx2)] overflow-hidden text-ellipsis whitespace-nowrap">
                {sk.concept?.length > 32 ? sk.concept.substring(0,30)+'…' : sk.concept}
              </span>
            </div>
          ))}
          {mappedSkills.length > 2 && (
            <div className="text-[9px] text-[var(--tx3)] pl-1">+{mappedSkills.length-2} more</div>
          )}
        </div>
      )}
      
      {/* Coverage bar */}
      <div className="h-[3px] rounded bg-[var(--bg4)]/20 overflow-hidden mb-1">
        <div className="h-full rounded transition-all"
          style={{ width:`${Math.min(100, (mappedSkills.length+(course.skill_count||0))*8)}%`,
                   background: coverageType==='direct' ? '#22c55e' : coverageType==='partial' ? '#f59e0b' : '#3b82f6' }} />
      </div>
      
      {/* Meta */}
      <div className="text-[9px] font-mono text-[var(--tx3)]">
        {mappedSkills.length || course.skill_count || 0} skill{ (mappedSkills.length || course.skill_count) !== 1 ? 's' : ''} · {course.co_count ?? '?'} COs
        {allSkills.length > mappedSkills.length && trackFilter !== 'none' &&
          <span className="text-[var(--tx4)]"> · {allSkills.length - mappedSkills.length} others</span>
        }
      </div>
    </div>
  );
}
