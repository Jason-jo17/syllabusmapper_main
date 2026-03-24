"use client";
import { useState, useEffect } from "react";
import { GapItem } from "@/components/gap/GapItem";
import { SemesterRecommendations } from "@/components/gap/SemesterRecommendations";
import type { SkillNode } from "@/lib/types";

interface GapReport {
  gaps: SkillNode[];
  priority_gaps: Array<{ skill_id: string; priority: string }>;
  coverage_pct: number;
}

interface JobRole {
  id: string;
  role_name: string;
}

export default function GapAnalysisPage() {
  const [report, setReport] = useState<GapReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const syllabusId = "ece00000-0000-0000-0000-000000000000";
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    // 1. Get Job Role (Defaulting to the one we synced)
    fetch(`${apiUrl}/api/colleges/roles`) // Assuming this lists roles
      .then(r => r.json())
      .then((roles: JobRole[]) => {
        const role = roles.find(r => r.role_name === "Embedded Electronics Engineer");
        if (!role) return;

        // 2. Trigger Analysis
        fetch(`${apiUrl}/api/gap/analyse`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ syllabus_id: syllabusId, job_role_id: role.id })
        })
        .then(r => r.json())
        .then((data: GapReport) => {
            setReport(data);
            setLoading(false);
        });
      })
      .catch(err => {
        console.error("Gap fetch failed:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-[var(--tx2)]">Analysing curriculum gaps...</div>;

  const gaps = report?.gaps || [];
  const priorityGaps = report?.priority_gaps || [];

  return (
    <div className="p-8 pb-32 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#e2e6f8] mb-2">Gap Analysis</h1>
        <p className="text-[#8b93b8]">
            {report?.coverage_pct?.toFixed(1)}% Coverage · {gaps.length} Skills with no CO coverage.
        </p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-2">
          {gaps.length === 0 ? (
            <div className="p-8 bg-[var(--bg1)] rounded-xl border border-[var(--bd)] text-center text-[var(--tx3)]">
                All skills are covered by the current curriculum!
            </div>
          ) : (
            gaps.slice(0, 15).map((skill: SkillNode) => {
                const priority = (priorityGaps.find(p => p.skill_id === skill.id)?.priority || 'Medium') as 'Critical' | 'High' | 'Medium' | 'Low';
                return <GapItem key={skill.id} skill={skill} priority={priority} />;
            })
          )}
        </div>
        <div>
          <SemesterRecommendations />
        </div>
      </div>
    </div>
  );
}
