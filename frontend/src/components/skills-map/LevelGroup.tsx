"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { SkillCard } from "./SkillCard";
import type { SkillNode, Event } from "@/lib/types";

interface Props {
  level: string;
  skills: SkillNode[];
  allEvents?: Event[];
}

const LEVEL_COLORS: Record<string, string> = {
  L0:'#f59e0b', L1:'#3b82f6', L2:'#22c55e', L3:'#a855f7', L4:'#f43f5e', L5:'#06b6d4'
};

export function LevelGroup({ level, skills, allEvents = [] }: Props) {
  const [expanded, setExpanded] = useState(true);
  const color = LEVEL_COLORS[level] || '#6366f1';
  
  // Group by Knowledge Set
  const ksGrouped = skills.reduce((acc, skill) => {
    const ks = skill.knowledge_set || 'General';
    if (!acc[ks]) acc[ks] = [];
    acc[ks].push(skill);
    return acc;
  }, {} as Record<string, SkillNode[]>);

  return (
    <div className="mb-6">
      <div 
        className="flex items-center justify-between p-3 rounded-t-lg border border-[var(--bd)] border-b-0 cursor-pointer transition-colors duration-200"
        style={{ backgroundColor: `${color}18` }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-[14px] font-mono font-bold" style={{ color }}>{level}</span>
          <span className="text-[12px] text-[var(--tx)] font-semibold">{skills.length} Skills</span>
        </div>
        <div className="text-[var(--tx2)]">
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>
      
      {expanded && (
        <div className="p-4 border border-[var(--bd)] rounded-b-lg bg-[var(--bg1)]/60 backdrop-blur-sm">
          {Object.entries(ksGrouped).map(([ks, ksSkills]: [string, SkillNode[]]) => (
            <div key={ks} className="mb-6 last:mb-0">
              <h3 className="text-[11px] font-mono text-[var(--tx3)] uppercase tracking-widest mb-3 pb-1 border-b border-[var(--bd)]">
                {ks}
              </h3>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                {ksSkills.map(skill => (
                  <SkillCard key={skill.id} skill={skill} allEvents={allEvents} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
