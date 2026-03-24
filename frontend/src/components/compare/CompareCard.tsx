"use client";

interface RoleStats {
  roleName: string;
  levels: { L0: number; L1: number; L2: number; L3: number; L4: number; L5: number };
}

export function CompareCard({ role, stats }: { role: string; stats: RoleStats }) {
  const max = Math.max(...Object.values(stats.levels), 1);
  const colors = { L0:'#f59e0b', L1:'#3b82f6', L2:'#22c55e', L3:'#a855f7', L4:'#f43f5e', L5:'#06b6d4' };

  return (
    <div className="bg-[#14172a] border border-[#232640] rounded-lg p-5">
      <h3 className="text-[#e2e6f8] font-bold text-sm mb-5">{role}</h3>
      <div className="space-y-3.5">
        {(Object.entries(stats.levels) as [keyof typeof colors, number][]).map(([lvl, count]) => (
          <div key={lvl} className="flex items-center gap-3">
            <span className="text-[11px] font-mono font-bold text-[#8b93b8] w-5">{lvl}</span>
            <div className="flex-1 h-2.5 bg-[#09090f] rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${(count / max) * 100}%`, backgroundColor: colors[lvl] }}
              />
            </div>
            <span className="text-[11px] font-mono text-[#e2e6f8] w-6 text-right">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
