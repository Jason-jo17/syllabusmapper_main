export function SemesterRecommendations() {
  return (
    <div className="bg-[rgba(99,102,241,0.05)] border border-[#6366f1] rounded-lg p-5">
      <h3 className="text-[#e2e6f8] font-bold mb-2">Automated Recommendations</h3>
      <p className="text-[12px] text-[#8b93b8] mb-4">
        To address critical gaps, SyllabusMapper suggests the following curriculum adjustments:
      </p>
      <ul className="space-y-3 text-[12px] text-[#e2e6f8]">
        <li className="flex gap-3 items-start">
          <span className="text-[#6366f1] mt-0.5 text-[14px]">●</span>
          <span><strong>Year 2 / Sem 4:</strong> Introduce practical debugging tools (GDB, JTAG) into <span className="font-mono text-[#818cf8]">Microcontroller Lab</span> to cover L2 Execution gaps.</span>
        </li>
        <li className="flex gap-3 items-start">
          <span className="text-[#6366f1] mt-0.5 text-[14px]">●</span>
          <span><strong>Year 3 / Sem 5:</strong> Add CI/CD and version control collaboration directly into the <span className="font-mono text-[#818cf8]">Mini Project</span> rubric.</span>
        </li>
      </ul>
    </div>
  );
}
