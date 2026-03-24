"use client";
import { useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

export function IngestionStatus({ syllabusId, onComplete }: { syllabusId: string, onComplete: ()=>void }) {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    // Simulate polling for demo purposes since backend isn't connected
    const t1 = setTimeout(() => setStage(1), 1500);
    const t2 = setTimeout(() => setStage(2), 3500);
    const t3 = setTimeout(() => setStage(3), 5500);
    const t4 = setTimeout(() => { setStage(4); onComplete(); }, 7500);

    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); clearTimeout(t4); };
  }, [syllabusId, onComplete]);

  const steps = [
    { label: "Extracting text & OCR", desc: "Layered extraction via PyPDF & Claude Vision" },
    { label: "Semantic Parsing", desc: "Structuring topics & identifying Course Outcomes" },
    { label: "Embedding Generation", desc: "Vectorizing COs with Voyage AI voyage-3" },
    { label: "AI Skill Mapping", desc: "pgvector similarity + Claude reranking logic" },
  ];

  return (
    <div className="bg-[#14172a] border border-[#232640] rounded-xl p-8 max-w-2xl mx-auto shadow-xl">
      <h3 className="text-[#e2e6f8] font-bold text-lg mb-8 text-center">Analysing Curriculum Pipeline</h3>
      <div className="space-y-6">
        {steps.map((s, i) => {
          const isPast = stage > i;
          const isCurrent = stage === i;
          return (
            <div key={i} className="flex gap-4">
              <div className="mt-0.5">
                {isPast ? (
                  <CheckCircle2 className="text-[#22c55e]" size={20} />
                ) : isCurrent ? (
                  <Loader2 className="animate-spin text-[#6366f1]" size={20} />
                ) : (
                  <Circle className="text-[#454e72]" size={20} />
                )}
              </div>
              <div className={isPast || isCurrent ? "opacity-100" : "opacity-40 transition-opacity"}>
                <div className={`text-[14px] font-bold ${isCurrent ? 'text-[#6366f1]' : 'text-[#e2e6f8]'}`}>
                  {s.label}
                </div>
                <div className="text-[12px] text-[#8b93b8] mt-0.5">{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
