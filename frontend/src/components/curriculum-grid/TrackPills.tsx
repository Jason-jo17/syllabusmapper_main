"use client";
interface Props {
  activeFilter: 'none' | 'ece' | 'l0l1' | 'l2l3' | 'l4l5';
  onChange: (f: 'none' | 'ece' | 'l0l1' | 'l2l3' | 'l4l5') => void;
}

export function TrackPills({ activeFilter, onChange }: Props) {
  const pills = [
    { value: 'none', label: 'All Courses' },
    { value: 'ece', label: 'Career Track: Embedded EE' },
    { value: 'l0l1', label: 'L0-L1 Foundation' },
    { value: 'l2l3', label: 'L2-L3 Execution' },
    { value: 'l4l5', label: 'L4-L5 Leadership' },
  ] as const;

  return (
    <div className="flex gap-2 mb-2 overflow-x-auto pb-2 scrollbar-none">
      {pills.map(p => (
        <button
          key={p.value}
          onClick={() => onChange(p.value)}
          className={`px-3 py-1.5 rounded-full text-[11px] font-medium transition-colors border whitespace-nowrap ${
            activeFilter === p.value
              ? 'bg-[var(--glow)] text-[var(--acc2)] border-[var(--acc)]'
              : 'bg-[var(--bg2)] text-[var(--tx2)] border-[var(--bd)] hover:border-[var(--acc)] hover:text-[var(--tx)]'
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
