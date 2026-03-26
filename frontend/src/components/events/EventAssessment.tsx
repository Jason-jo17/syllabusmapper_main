"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Save, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { API_URL } from "@/lib/config";

interface SkillAddressed {
  knowledge_set: string;
  skill_knowledge: string;
  bl_level: string;
}

interface SavedAssignment {
  [skillKey: string]: { mq: number[]; sq: number[]; rub: number[] };
}

interface Event {
  id: string;
  event_name: string;
  organizing_body: string;
  description: string;
  knowledge_domain_1: string;
  skills_addressed: SkillAddressed[];
}

interface Assessment {
  s: string;
  ks: string;
  d: string;
  bl: number;
  bln: string;
  mq: string[];
  sq: string[];
  sh: string[];
  rub: Array<Array<{ el: string; desc: string; s5: string; s4: string; s3: string; s2: string; s1: string }>>;
}

export function EventAssessment() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;

  const [eventData, setEventData] = useState<Event | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  
  // selection state: { skillName_blLevel: { mq: [indexes], sq: [indexes], rub: [indexes] } }
  const [selection, setSelection] = useState<SavedAssignment>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        
        // 1. Fetch event first to know which skills to fetch assessments for
        const evRes = await fetch(`${API_URL}/api/events/${eventId}`);
        const ev = await evRes.json();
        setEventData(ev);

        // 2. Fetch assessments for each skill in parallel
        const skillNames = ev.skills_addressed?.map((s: SkillAddressed) => s.skill_knowledge) || [];
        const uniqueSkills = Array.from(new Set(skillNames)) as string[];
        
        const [assResults, savedAss] = await Promise.all([
          Promise.all(uniqueSkills.map(s => 
            fetch(`${API_URL}/api/assessments?skill=${encodeURIComponent(s)}`).then(r => r.json())
          )),
          fetch(`${API_URL}/api/assignments/${eventId}`).then(r => r.json())
        ]);
        
        // Flatten and deduplicate assessments
        const allAss = assResults.flat();
        const seen = new Set();
        const dedupedAss = allAss.filter((a: Assessment) => {
          const key = `${a.s}-${a.bl}`;
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });

        setAssessments(dedupedAss);
        
        if (savedAss && Object.keys(savedAss).length > 0 && !savedAss.error) {
            setSelection(savedAss);
        }
      } catch (e) {
        console.error("Error fetching data", e);
      } finally {
        setLoading(false);
      }
    }
    if (eventId) fetchData();
  }, [eventId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`${API_URL}/api/assignments/${eventId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selection),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const toggleSelection = (skillKey: string, type: "mq" | "sq" | "rub", index: number) => {
    setSelection(prev => {
      const current = prev[skillKey] || { mq: [], sq: [], rub: [] };
      const arr = current[type];
      const newArr = arr.includes(index) ? arr.filter(i => i !== index) : [...arr, index];
      return { ...prev, [skillKey]: { ...current, [type]: newArr } };
    });
  };

  if (loading) return <div className="p-8 text-[var(--tx2)] animate-pulse">Loading assessment data...</div>;
  if (!eventData) return <div className="p-8">Event not found</div>;

  return (
    <div className="max-w-4xl mx-auto pb-32">
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => router.back()} className="flex items-center gap-2 -ml-4">
          <ArrowLeft size={16} /> Back to Events
        </Button>
        <Button onClick={handleSave} disabled={saving} className="flex items-center gap-2 bg-[var(--acc)] text-black hover:bg-[var(--acc2)]">
          {saved ? <CheckCircle2 size={16} /> : <Save size={16} />}
          {saving ? "Saving..." : saved ? "Saved!" : "Save Assignment"}
        </Button>
      </div>

      <div className="bg-[var(--bg2)] border border-[var(--bd)] rounded-xl p-6 mb-8">
        <h1 className="text-2xl font-bold text-[var(--tx)] mb-2">{eventData.event_name}</h1>
        <p className="text-[var(--tx2)] text-sm mb-4">{eventData.organizing_body}</p>
        <p className="text-[var(--tx)] text-sm leading-relaxed">{eventData.description}</p>
      </div>

      <h2 className="text-lg font-semibold text-[var(--tx)] mb-4">Configure Assessments for Skills</h2>

      <div className="space-y-6">
        {eventData.skills_addressed?.map((skill, idx) => {
          const matchingAsses = assessments.filter(a => a.s.toLowerCase().includes(skill.skill_knowledge?.toLowerCase()) || skill.skill_knowledge?.toLowerCase().includes(a.s.toLowerCase()));
          
          if (matchingAsses.length === 0) return null;

          return matchingAsses.map((ass, aIdx) => {
            const skillKey = `${ass.s}_${ass.bl}`;
            const sel = selection[skillKey] || { mq: [], sq: [], rub: [] };

            return (
              <div key={`${idx}-${aIdx}`} className="bg-[var(--bg1)] border border-[var(--bd)] rounded-xl overflow-hidden">
                <div className="bg-[var(--bg2)] p-4 border-b border-[var(--bd)] flex items-center justify-between sticky top-0 z-10">
                  <div>
                    <h3 className="font-semibold text-[var(--tx)]">{ass.s}</h3>
                    <p className="text-xs text-[var(--tx2)]">{ass.ks}</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded bg-[var(--bg3)] text-[var(--tx2)] border border-[var(--bd)]">
                    BL{ass.bl}: {ass.bln}
                  </span>
                </div>

                <div className="p-4 space-y-8">
                  {/* MCQs */}
                  {ass.mq && ass.mq.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-[var(--tx)] mb-3 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[var(--acc)]"></div> Multiple Choice Questions
                      </h4>
                      <div className="grid gap-2">
                        {ass.mq.map((q, qIdx) => (
                          <label key={qIdx} className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer border transition-colors ${sel.mq.includes(qIdx) ? 'border-[var(--acc)] bg-[rgba(232,150,12,0.1)]' : 'border-[var(--bd)] hover:bg-[var(--bg2)]'}`}>
                            <input type="checkbox" checked={sel.mq.includes(qIdx)} onChange={() => toggleSelection(skillKey, 'mq', qIdx)} className="mt-0.5" />
                            <span className={`text-sm ${sel.mq.includes(qIdx) ? 'text-[var(--acc2)]' : 'text-[var(--tx)]'}`}>{q}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* SQs */}
                  {ass.sq && ass.sq.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-[var(--tx)] mb-3 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#a78bfa]"></div> Subjective Questions
                      </h4>
                      <div className="grid gap-2">
                        {ass.sq.map((q, qIdx) => (
                          <label key={qIdx} className={`flex flex-col gap-2 p-3 rounded-lg cursor-pointer border transition-colors ${sel.sq.includes(qIdx) ? 'border-[#a78bfa] bg-[rgba(167,139,250,0.1)]' : 'border-[var(--bd)] hover:bg-[var(--bg2)]'}`}>
                            <div className="flex items-start gap-3">
                                <input type="checkbox" checked={sel.sq.includes(qIdx)} onChange={() => toggleSelection(skillKey, 'sq', qIdx)} className="mt-0.5" />
                                <span className={`text-sm ${sel.sq.includes(qIdx) ? 'text-[#a78bfa]' : 'text-[var(--tx)]'}`}>{q}</span>
                            </div>
                            {ass.sh && ass.sh[qIdx] && (
                                <div className="ml-6 text-xs text-[var(--tx3)] italic border-l-2 border-[#a78bfa] pl-2 py-1">Hint: {ass.sh[qIdx]}</div>
                            )}
                          </label>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rubrics */}
                  {ass.rub && ass.rub.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-[var(--tx)] mb-3 flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#22c55e]"></div> Evaluation Rubrics
                      </h4>
                      <div className="grid gap-4">
                        {ass.rub.map((rubricSet, rIdx) => (
                           <div key={rIdx} className={`p-4 rounded-xl border transition-colors ${sel.rub.includes(rIdx) ? 'border-[#22c55e] bg-[rgba(34,197,94,0.05)]' : 'border-[var(--bd)] bg-[var(--bg2)]'}`}>
                             <div className="flex items-center gap-3 mb-4">
                                <input type="checkbox" checked={sel.rub.includes(rIdx)} onChange={() => toggleSelection(skillKey, 'rub', rIdx)} />
                                <h5 className="font-medium text-[var(--tx)] text-sm">Rubric Set {rIdx + 1}</h5>
                             </div>
                             <div className="space-y-4 pl-6">
                               {rubricSet.map((r, i) => (
                                 <div key={i} className="text-xs">
                                    <p className="font-semibold text-[var(--tx)] mb-1">{r.el}</p>
                                    <p className="text-[var(--tx2)] mb-2 italic">{r.desc}</p>
                                    <div className="grid grid-cols-5 gap-2 mt-2">
                                        <div className="bg-[var(--bg3)] p-2 rounded"><div className="text-[#22c55e] font-bold mb-1">5</div>{r.s5}</div>
                                        <div className="bg-[var(--bg3)] p-2 rounded"><div className="text-[#34d399] font-bold mb-1">4</div>{r.s4}</div>
                                        <div className="bg-[var(--bg3)] p-2 rounded"><div className="text-[var(--acc2)] font-bold mb-1">3</div>{r.s3}</div>
                                        <div className="bg-[var(--bg3)] p-2 rounded"><div className="text-[#fb923c] font-bold mb-1">2</div>{r.s2}</div>
                                        <div className="bg-[var(--bg3)] p-2 rounded"><div className="text-red-400 font-bold mb-1">1</div>{r.s1}</div>
                                    </div>
                                 </div>
                               ))}
                             </div>
                           </div>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              </div>
            );
          });
        })}
      </div>
    </div>
  );
}
