import { CompareCard } from "@/components/compare/CompareCard";

export default function CompareRolesPage() {
  const stats1 = { roleName: 'Embedded EE', levels: { L0: 34, L1: 22, L2: 45, L3: 12, L4: 8, L5: 2 } };
  const stats2 = { roleName: 'Software Dev', levels: { L0: 20, L1: 30, L2: 40, L3: 35, L4: 15, L5: 5 } };
  const stats3 = { roleName: 'Data Engineer', levels: { L0: 15, L1: 25, L2: 30, L3: 20, L4: 10, L5: 5 } };

  return (
    <div className="p-8 pb-32 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#e2e6f8] mb-2">Compare Roles</h1>
        <p className="text-[#8b93b8]">Side-by-side level distribution for all career tracks.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <CompareCard role="Embedded Electronics Engineer" stats={stats1} />
        <CompareCard role="Software Developer" stats={stats2} />
        <CompareCard role="Data Engineer" stats={stats3} />
      </div>
    </div>
  );
}
