import { Suspense } from "react";
import { CurriculumGrid } from "@/components/curriculum-grid/CurriculumGrid";

export default function CurriculumGridPage() {
  return (
    <div className="h-full relative">
      <Suspense fallback={<div className="p-8 text-[var(--tx2)]">Loading curriculum grid...</div>}>
        <CurriculumGrid />
      </Suspense>
    </div>
  );
}
