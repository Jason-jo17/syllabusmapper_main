import type { SkillNode } from "@/lib/types";

export function GapItem({ skill, priority }: { skill: SkillNode, priority: 'Critical'|'High'|'Medium'|'Low' }) {
  const colors = {
    Critical: 'text-[#ef4444] bg-[rgba(239,68,68,0.1)] border-[#ef4444]',
    High: 'text-[#f59e0b] bg-[rgba(245,158,11,0.1)] border-[#f59e0b]',
    Medium: 'text-[#3b82f6] bg-[rgba(59,130,246,0.1)] border-[#3b82f6]',
    Low: 'text-[#8b93b8] bg-[#1a1d32] border-[#232640]'
  };

  return (
    <div className="p-3 bg-[#14172a] border border-[#232640] rounded-lg mb-3 flex gap-4 items-start">
      <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border ${colors[priority]} mt-0.5 whitespace-nowrap`}>
        {priority}
      </div>
      <div>
        <div className="text-[13px] font-bold text-[#e2e6f8] mb-1">{skill.concept}</div>
        <div className="text-[11px] text-[#8b93b8] leading-relaxed mb-2">{skill.skill_description}</div>
        <div className="text-[10px] font-mono text-[#454e72] flex gap-2 flex-wrap">
          <span className="px-1.5 rounded" style={{ background: 'rgba(255,255,255,0.05)' }}>{skill.level}</span>
          <span className="px-1.5 rounded" style={{ background: 'rgba(255,255,255,0.05)' }}>{skill.knowledge_set}</span>
          {skill.tools && skill.tools !== '-' && (
            <span className="text-[#818cf8] px-1.5 rounded" style={{ background: 'rgba(99,102,241,0.1)' }}>🔧 {skill.tools}</span>
          )}
        </div>
      </div>
    </div>
  );
}
