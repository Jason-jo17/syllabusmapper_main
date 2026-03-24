import { SkillsMap } from "@/components/skills-map/SkillsMap";

export default function SkillsMapPage() {
  return (
    <div className="p-8 pb-32">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#e2e6f8] mb-2">L0–L5 Skills Map</h1>
        <p className="text-[#8b93b8]">Comprehensive mapping of industry concepts, skills, and tools across levels.</p>
      </div>
      <SkillsMap role="Embedded Electronics Engineer" />
    </div>
  );
}
