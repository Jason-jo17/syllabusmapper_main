"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Calendar } from "lucide-react";
import { COSlot } from "./COSlot";
import type { SkillNode, Event, SkillAddressed } from "@/lib/types";

interface Props {
  skill: SkillNode;
  allEvents?: Event[];
}

export function SkillCard({ skill, allEvents = [] }: Props) {
  const [expanded, setExpanded] = useState(false);

  const skillEvents = allEvents.filter(ev => 
    ev.skills_addressed?.some((es: SkillAddressed) => 
      skill.concept && es.knowledge_set && skill.concept.toLowerCase().includes(es.knowledge_set.toLowerCase())
    )
  );

  return (
    <div className="border border-[var(--bd)] rounded-lg bg-[var(--bg1)] overflow-hidden mb-3 hover:border-[var(--acc)] transition-all duration-200 shadow-sm">
      <div 
        className="p-3 flex justify-between items-start cursor-pointer hover:bg-[var(--bg2)]/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1 min-w-0 pr-4">
          <div className="text-[13px] font-bold text-[var(--tx)] mb-1">{skill.concept}</div>
          <div className="text-[11px] text-[var(--tx2)] mb-2 leading-relaxed">{skill.skill_description}</div>
          <div className="flex gap-2 font-mono text-[9px] text-[var(--tx3)] flex-wrap">
            <span>BL{skill.bloom_level}</span>
            <span>·</span>
            <span>{skill.task_type}</span>
            {skill.tools && skill.tools !== '-' && (
              <>
                <span>·</span>
                <span className="text-[var(--acc2)] font-semibold">🔧 {skill.tools}</span>
              </>
            )}
            {skillEvents.length > 0 && (
              <>
                <span>·</span>
                <span className="text-[#f59e0b] font-semibold flex items-center gap-1">
                  <Calendar size={10} /> {skillEvents.length} Event{skillEvents.length > 1 ? 's' : ''}
                </span>
              </>
            )}
          </div>
        </div>
        <div className="text-[var(--tx3)] mt-1">
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>
      
      {expanded && (
        <div className="p-3 border-t border-[var(--bd)] bg-[var(--bg)]/40">
          <div className="text-[10px] uppercase tracking-widest text-[var(--tx3)] mb-2 font-mono">Mapped Course Outcomes</div>
          {(!skill.co_primary_text && !skill.co_secondary_text && !skill.co_tertiary_text) ? (
            <div className="text-[11px] text-[var(--tx3)] italic mb-4">No Course Outcomes mapped to this skill yet.</div>
          ) : (
            <div className="space-y-1 mb-4">
              <COSlot type="Primary" text={skill.co_primary_text} courseTitle={skill.co_primary_course} year={skill.co_primary_year} semester={skill.co_primary_sem} />
              <COSlot type="Secondary" text={skill.co_secondary_text} courseTitle={skill.co_secondary_course} year={skill.co_secondary_year} semester={skill.co_secondary_sem} />
              <COSlot type="Tertiary" text={skill.co_tertiary_text} courseTitle={skill.co_tertiary_course} year={skill.co_tertiary_year} semester={skill.co_tertiary_sem} />
            </div>
          )}

          {skillEvents.length > 0 && (
            <div>
              <div className="text-[10px] uppercase tracking-widest text-[#f59e0b] mb-2 font-mono mt-4 border-t border-[var(--bd)] pt-4 flex items-center gap-1.5">
                <Calendar size={12} /> Related Events ({skillEvents.length})
              </div>
              <div className="space-y-2">
                {skillEvents.map((ev, i) => (
                  <div key={ev.id || i} className="bg-[var(--bg1)] border border-[var(--bd)] rounded flex justify-between p-2">
                    <div>
                      <div className="text-[11px] text-[var(--tx)] font-semibold leading-tight mb-0.5">{ev.event_name}</div>
                      <div className="text-[9px] text-[var(--tx3)]">{ev.organizing_body}</div>
                    </div>
                    <span className="text-[9px] font-medium px-1.5 py-0.5 rounded bg-[rgba(245,158,11,0.1)] text-[#f59e0b] self-start border border-[rgba(245,158,11,0.2)]">
                      {ev.event_type}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
