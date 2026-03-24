interface COSlotProps {
  type: "Primary" | "Secondary" | "Tertiary";
  courseTitle?: string;
  year?: string;
  semester?: string;
  text?: string;
}

export function COSlot({ type, courseTitle, year, semester, text }: COSlotProps) {
  if (!text) return null;
  return (
    <div className="border border-[var(--bd)] rounded bg-[var(--bg2)]/50 p-2.5 mt-2 transition-colors duration-200">
      <div className="text-[10px] font-mono text-[var(--acc)] mb-1 font-bold">{type} Mapping</div>
      <div className="flex gap-2 text-[11px] text-[var(--tx)] font-semibold mb-1 flex-wrap">
        <span>{courseTitle || 'Unknown Course'}</span>
        <span className="text-[var(--tx3)]">· Year {year || '-'}</span>
        <span className="text-[var(--tx3)]">· Sem {semester || '-'}</span>
      </div>
      <div className="text-[11px] text-[var(--tx2)] leading-relaxed italic border-l-2 border-[var(--glow)] pl-2 py-0.5">
        {text}
      </div>
    </div>
  );
}
