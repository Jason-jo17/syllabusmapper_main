"use client";

import { useState, useEffect } from "react";
import { LevelGroup } from "./LevelGroup";
import type { SkillNode, Event } from "@/lib/types";
import { Search } from "lucide-react";
import { API_URL } from "@/lib/config";

export function SkillsMap({ role }: { role: string }) {
  const [skills, setSkills] = useState<SkillNode[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [allEvents, setAllEvents] = useState<Event[]>([]);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/skills/?role=${role}`)
      .then(r => r.json())
      .then(data => {
        setSkills(data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    fetch(`${API_URL}/api/events/`)
      .then(r => r.json())
      .then(data => setAllEvents(data || []))
      .catch(err => console.error(err));
  }, [role]);

  const filtered = skills.filter(s => {
    const conceptMatch = (s.concept || "").toLowerCase().includes(search.toLowerCase());
    const descMatch = (s.skill_description || "").toLowerCase().includes(search.toLowerCase());
    const toolsMatch = (s.tools || "").toLowerCase().includes(search.toLowerCase());
    return conceptMatch || descMatch || toolsMatch;
  });

  const levels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5'];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-2.5 text-[var(--tx3)]" size={18} />
        <input 
          type="text" 
          placeholder="Search skills, concepts, or tools..." 
          className="w-full bg-[var(--bg2)]/50 border border-[var(--bd)] text-[var(--tx)] rounded-lg pl-10 pr-4 py-2 focus:outline-none focus:border-[var(--acc)] transition-all"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="text-center py-10 text-[#8b93b8]">Loading skills map...</div>
      ) : (
        <div className="space-y-4">
          {levels.map(lvl => {
            const lvlSkills = filtered.filter(s => s.level === lvl);
            if (lvlSkills.length === 0) return null;
            return <LevelGroup key={lvl} level={lvl} skills={lvlSkills} allEvents={allEvents} />;
          })}
        </div>
      )}
    </div>
  );
}
